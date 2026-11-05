"""Protect the actual native stat-pointer and sprite integration boundary."""
import json,struct,unittest
import battle_ui_patch as b
from elf import ROOT,Elf
from extract import pack_members
from test_binary import Cpu


class BattleUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=(ROOT/'work/output/v0.2.2/SLPS_250.70').read_bytes()
        cls.elf=Elf(b.patch_elf(cls.base))
        cls.before=Elf(cls.base)
        cls.pack=(ROOT/'work/output/v0.2.2/00022.pack').read_bytes()

    def test_native_pointer_pair_reaches_complete_format_without_truncation(self):
        # Execute the emitted signed LUI/addiu address pair, not a Python-only
        # address calculation. This catches the 0xA000 sign extension boundary.
        c=Cpu();c.put(0x1497B8,self.elf.at(0x1497B8,4));c.put(0x1497BC,bytes(4))
        c.put(0x1497C0,self.elf.at(0x1497C0,4))
        c.put(0x1497C4,struct.pack('<2I',0x03E00008,0))
        c.reg('ra',0xFFFF0000);c.run(0x1497B8)
        self.assertEqual(c.r[5],b.BASE)
        text=b.language()['status']['en'];self.assertEqual(self.elf.at(b.BASE,len(text.encode('cp932'))+1),text.encode('cp932')+b'\0')
        original=self.before.at(b.FORMAT,136)
        self.assertEqual(self.elf.at(b.FORMAT,136),original)
        self.assertEqual(b.signature(text),b.signature(original[:-1].decode('cp932')))
        # Simulate native printf with both actual L/M runtime strings, percent
        # selectors and three-digit values. Never consumes %0.
        for letter in ('L','M'):
            result=text%(999,letter,999,letter,100,100,100,100,100)
            self.assertEqual(result.count('\n'),6)
            self.assertIn('%1Cannon%0',result)
            self.assertLess(len(result.encode('cp932')),256)

    def test_old_loaded_segment_and_every_speaker_record_retained(self):
        for s in self.before.segments:
            if s[0]!=1:continue
            expected=bytearray(self.before.at(s[2],s[4]));actual=bytearray(self.elf.at(s[2],s[4]))
            for va in (0x1497B8,0x1497C0):
                if s[2]<=va<s[2]+s[4]:actual[va-s[2]:va-s[2]+4]=expected[va-s[2]:va-s[2]+4]
            self.assertEqual(actual,expected)

    def test_only_seven_pixel_planes_change_in_resource_pack(self):
        after,_=b.patch_pack(self.pack)
        def members(p):return {m['id']:p[m['offset']:m['offset']+m['size']] for m in pack_members(p)}
        old,new=members(self.pack),members(after)
        self.assertEqual(old.keys(),new.keys());changed=[]
        for mid in old:
            if old[mid]==new[mid]:continue
            changed.append(mid)
            self.assertEqual(old[mid][:320],new[mid][:320])
            self.assertEqual(old[mid][1344:],new[mid][1344:])
            for i,(x,y) in enumerate(zip(old[mid][320:1344],new[mid][320:1344])):
                if i%64<12 or i%64>=56:self.assertEqual(x,y)
            ix=[v for q in new[mid][320:1344] for v in (q&15,q>>4)]
            self.assertNotIn(5,ix) # no unreadable orange source lettering left
            self.assertIn(7,ix) # native opaque white fill
        self.assertEqual(changed,list(range(10059,10066)))

    def test_reject_modified_sources_and_repeat_application(self):
        with self.assertRaises(ValueError):b.patch_elf(self.elf.data)
        patched,_=b.patch_pack(self.pack)
        with self.assertRaises(ValueError):b.patch_pack(patched)


if __name__=='__main__':unittest.main()
