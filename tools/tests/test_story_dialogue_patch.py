import json,struct,unittest
from test_binary import ROOT
from elf import Elf
from extract import pack_members
from textcodec import parse_table,encode
from message_pages import pages
import story_dialogue_patch as story

def members(b):return {m['id']:b[m['offset']:m['offset']+m['size']]for m in pack_members(b)}

class LaterStoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data,cls.packs,cls.overlays,cls.report=story.inputs()
        cls.base=(ROOT/'work/output/v0.2.19/SLPS_250.70').read_bytes()

    def test_all_finite_rows_and_original_calls_words_and_voice_sequences(self):
        count=bodies=0
        for t in story.language()['tables']:
            pn,mid=map(int,t['table'].split('_'));source=members((ROOT/f'work/source/afs/RESOURCE/{pn:05d}.bin').read_bytes())[mid]
            old=parse_table(source);new=parse_table(members(self.packs[pn])[mid]);self.assertEqual(len(old),len(new));self.assertEqual([r['id']for r in t['rows']],list(range(len(old))))
            for r,a,b in zip(t['rows'],old,new):
                original,approved,built=pages(a),pages(encode(r['en'])),pages(b)
                self.assertEqual(len(original),len(built));self.assertEqual(len(approved),len(built))
                for x,y,z in zip(original,approved,built):
                    self.assertEqual({k:v for k,v in x.items()if k not in('start','end','body')},{k:v for k,v in z.items()if k not in('start','end','body')})
                    self.assertEqual(y['body'].split(),z['body'].split())
                    if z['flags']&1:bodies+=1;self.assertLess(len(z['body']),400)
                count+=1
        self.assertEqual(count,1135);self.assertEqual(bodies,5749)

    def test_existing_elf_hooks_and_unrelated_pack_members_remain_exact(self):
        original=bytearray(self.data);e=Elf(self.data)
        for pn in range(4906,4937):
            va=e.symbol('_pacfileA')['va']+pn*8+4;off=e.offset(va);self.assertEqual(int.from_bytes(self.data[off:off+4],'little'),len(self.packs[pn]));original[off:off+4]=self.base[off:off+4]
            path=ROOT/f'work/output/v0.2.19/{pn:05d}.pack'
            old=members(path.read_bytes()if path.exists()else(ROOT/f'work/source/afs/RESOURCE/{pn:05d}.bin').read_bytes());new=members(self.packs[pn]);self.assertEqual(set(old),set(new))
            for mid in old:
                if mid!=pn+5478:self.assertEqual(old[mid],new[mid])
        self.assertEqual(bytes(original),self.base)

    def test_reported_scene_present_and_choice_does_not_grow_original_dynamic_suffix(self):
        row=parse_table(members(self.packs[4914])[10392])[1]
        self.assertIn(b'Heh-heh!',row);self.assertIn(b'Chief Taiga',row);self.assertIn(b'Rikiya',row)
        voices=[p['voice']for p in pages(row)if p['flags']&1];self.assertEqual(voices,[9396,9397,9398,9399,9400])
        layout=self.report['story_dialogue']['native_layout'][-1]['native_layout'][0]
        self.assertLessEqual(layout['suffix_px'],layout['original_suffix_px']);self.assertEqual(layout['lines'][1:],['Yes','No'])

if __name__=='__main__':unittest.main()
