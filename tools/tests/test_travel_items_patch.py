"""Native parser, full-message fit, pack relocation and retained-game checks."""
import json,unittest
from elf import ROOT,Elf
from extract import pack_members
from textcodec import parse_table,controls,decode,encode
from message_pages import pages
import test_message_pages as native_parser
import travel_items_patch as b

class TravelItemsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base,cls.previous,cls.overlays,_=b.prior.inputs()
        cls.data,cls.packs,cls.report=b.patch(cls.base,cls.previous);cls.e=Elf(cls.data)

    def test_all529_calls_match_actual_native_control_parser(self):
        parser=native_parser.MessagePageTests();parser.elf=self.e;count=0
        for t in b.language()['tables']:
            pn,mid=map(int,t['table'].split('_'));pack=self.packs[pn];m=next(m for m in pack_members(pack) if m['id']==mid)
            rows=parse_table(pack[m['offset']:m['offset']+m['size']])
            for r in t['rows']:
                for p in pages(rows[r['id']]):
                    self.assertEqual(parser.native(rows[r['id']],p['start']),p,(t['table'],r['id'],p['start']));count+=1
        self.assertEqual(count,529)

    def test_all433_complete_bodies_fit_and_original_voice_order_is_kept(self):
        count=0
        for r in self.report['native_layout']:
            for p in r['native_layout']:
                self.assertLessEqual(len(p['lines']),3);self.assertLessEqual(max(p['widths']),504)
                self.assertLessEqual(p['prompt_right_px'],504);self.assertLess(p['body_bytes'],400);count+=1
        self.assertEqual(count,433)
        for t in b.language()['tables']:
            pn,mid=map(int,t['table'].split('_'));source=(ROOT/f'work/source/afs/RESOURCE/{pn:05d}.bin').read_bytes();new=self.packs[pn]
            get=lambda p:next(m for m in pack_members(p) if m['id']==mid)
            a,z=get(source),get(new);oldrows=parse_table(source[a['offset']:a['offset']+a['size']]);rows=parse_table(new[z['offset']:z['offset']+z['size']])
            for r in t['rows']:
                old,now=oldrows[r['id']],rows[r['id']]
                self.assertEqual(controls(decode(old)),controls(decode(now)))
                signature=lambda p:{k:v for k,v in p.items() if k not in ('start','end','body')}
                self.assertEqual(list(map(signature,pages(old))),list(map(signature,pages(now))))

    def test_cached_sizes_relocated_tables_and_all_other_assets_retained(self):
        for t in b.language()['tables']:
            pn,mid=map(int,t['table'].split('_'));old=self.previous.get(pn,(ROOT/f'work/source/afs/RESOURCE/{pn:05d}.bin').read_bytes());new=self.packs[pn]
            va=self.e.symbol('_pacfileA')['va']+pn*8+4;self.assertEqual(int.from_bytes(self.e.at(va,4),'little'),len(new))
            before=pack_members(old);after=pack_members(new);self.assertEqual([(m['id'],m['flags']) for m in before],[(m['id'],m['flags']) for m in after])
            for a,z in zip(before,after):
                if a['id']!=mid:self.assertEqual(old[a['offset']:a['offset']+a['size']],new[z['offset']:z['offset']+z['size']])
            self.assertTrue(all(a['offset']+a['size']<=z['offset'] for a,z in zip(after,after[1:])))
        for pn,pack in self.previous.items():
            if pn not in (23,4935,4950):self.assertEqual(self.packs[pn],pack)
        changed={int(k,16) for k in self.report['patched_words']};old=Elf(self.base)
        for s in old.segments:
            if s[0]!=1:continue
            va,size=s[2],s[4];a=old.at(va,size);z=bytearray(self.e.at(va,size))
            for site in changed:
                if va<=site<va+size:z[site-va:site-va+4]=a[site-va:site-va+4]
            self.assertEqual(bytes(z),a)
        with self.assertRaises(ValueError):b.patch(self.data,self.packs)

    def test_unsafe_unprofiled_controls_and_overflow_fail_without_truncation(self):
        widths=bytes(json.loads((ROOT/'work/output/v0.2.11/build_info.json').read_text('utf8'))['font_widths'])
        # A body using a color outside each exact source-derived profile is
        # refused; the new travel warning color does not broaden story input.
        text='\n{C:81930300}{C:819782830100}Warning.{C:819782830000}\n\n{x00}'
        with self.assertRaises(ValueError):b.stage_row(text,widths,'story')
        out,_=b.stage_row(text,widths,'travel-notice');self.assertEqual(controls(decode(out)),controls(text))
        with self.assertRaises(ValueError):b.stage_row('\n{C:81930300}'+('complete sentence '*100)+'\n\n{x00}',widths,'travel-notice')

if __name__=='__main__':unittest.main()
