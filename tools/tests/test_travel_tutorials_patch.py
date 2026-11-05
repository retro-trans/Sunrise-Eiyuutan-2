"""Complete category coverage, native parser and shared-pack preservation."""
import json,re,unittest
from elf import ROOT,Elf
from extract import pack_members
from textcodec import parse_table,decode,controls
from message_pages import pages
import test_message_pages as native_parser
import travel_tutorials_patch as b

class TravelTutorialsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base,cls.previous,cls.overlays,_=b.prior.inputs();cls.data,cls.packs,cls.report=b.patch(cls.base,cls.previous);cls.e=Elf(cls.data)

    def table(self,name):
        pn,mid=map(int,name.split('_'));pack=self.packs.get(pn,(ROOT/f'work/source/afs/RESOURCE/{pn:05d}.bin').read_bytes());m=next(m for m in pack_members(pack) if m['id']==mid)
        return parse_table(pack[m['offset']:m['offset']+m['size']])

    def test_complete_category_133_rows_855_bodies_have_no_japanese(self):
        rows=bodies=calls=0
        for item in self.report['category']['tables']:
            table=self.table(item['table']);self.assertEqual(len(table),item['rows']);rows+=len(table)
            for raw in table:
                ps=pages(raw);calls+=len(ps)
                for p in ps:
                    if p['flags']&1:
                        bodies+=1;self.assertIsNone(re.search('[ぁ-ゖァ-ヺ一-鿿]',p['body'].decode('cp932')),(item['table'],p['start']))
        self.assertEqual((rows,calls,bodies),(133,1242,855))

    def test_all1242_category_calls_match_actual_native_parser(self):
        parser=native_parser.MessagePageTests();parser.elf=self.e;count=0
        for item in self.report['category']['tables']:
            for raw in self.table(item['table']):
                for p in pages(raw):
                    self.assertEqual(parser.native(raw,p['start']),p,(item['table'],p['start']));count+=1
        self.assertEqual(count,1242)

    def test_new282_bodies_fit_with_original_voices_and_empty_calls(self):
        self.assertEqual(sum(len(r['native_layout']) for r in self.report['native_layout']),282)
        for r in self.report['native_layout']:
            for p in r['native_layout']:
                self.assertLessEqual(len(p['lines']),3);self.assertLessEqual(max(p['widths']),504);self.assertLessEqual(p['prompt_right_px'],504);self.assertLess(p['body_bytes'],400)
        for t in b.language()['tables']:
            source=json.loads((ROOT/f"work/source/text/{t['table']}.json").read_text('utf8'))['rows'];rows=self.table(t['table'])
            for r in t['rows']:self.assertEqual(controls(source[r['id']]['jp']),controls(decode(rows[r['id']])))

    def test_all_four_shared_travel_tables_survive_and_other_assets_match(self):
        self.assertEqual(self.report['resource_packs']['5611']['members'],[1235,1236,1237,1238])
        for pn in (4948,4951,5611):
            old=self.previous.get(pn,(ROOT/f'work/source/afs/RESOURCE/{pn:05d}.bin').read_bytes());new=self.packs[pn]
            before,after=pack_members(old),pack_members(new);replaced=self.report['resource_packs'][str(pn)]['members']
            self.assertEqual([(m['id'],m['flags']) for m in before],[(m['id'],m['flags']) for m in after])
            for a,z in zip(before,after):
                if a['id'] not in replaced:self.assertEqual(old[a['offset']:a['offset']+a['size']],new[z['offset']:z['offset']+z['size']])
            self.assertTrue(all(a['offset']+a['size']<=z['offset'] for a,z in zip(after,after[1:])))
        for pn,pack in self.previous.items():
            if pn not in (4948,4951,5611):self.assertEqual(self.packs[pn],pack)

    def test_loaded_code_retained_and_cached_sizes_guarded(self):
        changed={int(k,16) for k in self.report['patched_words']};old=Elf(self.base)
        for pn in (4948,4951,5611):
            va=self.e.symbol('_pacfileA')['va']+pn*8+4;self.assertEqual(int.from_bytes(self.e.at(va,4),'little'),len(self.packs[pn]))
        for s in old.segments:
            if s[0]!=1:continue
            va,size=s[2],s[4];before=old.at(va,size);after=bytearray(self.e.at(va,size))
            for p in changed:
                if va<=p<va+size:after[p-va:p-va+4]=before[p-va:p-va+4]
            self.assertEqual(bytes(after),before)
        with self.assertRaises(ValueError):b.patch(self.data,self.packs)

if __name__=='__main__':unittest.main()
