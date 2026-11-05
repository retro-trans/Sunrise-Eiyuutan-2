"""Protect the shared icon atlas boundary and all prior playable content."""
import unittest
import battle_icons_patch as b
from elf import ROOT,Elf
from extract import pack_members


def members(pack):
    return {m['id']:pack[m['offset']:m['offset']+m['size']] for m in pack_members(pack)}


class IconTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack=(ROOT/'work/output/v0.2.3/00022.pack').read_bytes()
        cls.after,_=b.patch_pack(cls.pack)
        cls.old=members(cls.pack);cls.new=members(cls.after)

    def test_only_target_member_and_eight_cells_change(self):
        self.assertEqual(len(self.pack),len(self.after))
        self.assertEqual([i for i in self.old if self.old[i]!=self.new[i]],[10051])
        def unpack(v):return [x for q in v[320:2368] for x in (q&15,q>>4)]
        old,new=unpack(self.old[10051]),unpack(self.new[10051])
        changed=set()
        for i,(a,c) in enumerate(zip(old,new)):
            self.assertEqual(a==4,c==4) # native transparent silhouette
            if a!=c:changed.add((i//64//16)*4+i%64//16)
        self.assertEqual(changed,{0,1,2,4,5,6,8,9})

    def test_source_colours_headers_and_cel_metadata_retained(self):
        a,c=self.old[10051],self.new[10051]
        self.assertEqual(a[:152],c[:152]) # header and six active source colours
        self.assertEqual(a[192:320],c[192:320])
        self.assertEqual(a[2368:],c[2368:])
        for i in range(6,16):self.assertEqual(c[128+i*4+3],128)

    def test_reject_repeated_or_modified_source(self):
        with self.assertRaises(ValueError):b.patch_pack(self.after)
        raw=bytearray(self.old[10051]);raw[320]^=1
        with self.assertRaises(ValueError):b.icon_member(raw)

    def test_complete_focused_build_keeps_previous_executable_and_all_other_packs(self):
        data,packs,report,_=b.inputs()
        self.assertEqual(data,(ROOT/'work/output/v0.2.3/SLPS_250.70').read_bytes())
        for n,p in packs.items():
            prior=(ROOT/f'work/output/v0.2.3/{n:05d}.pack').read_bytes()
            self.assertEqual(len(p),len(prior))
            if n!=22:self.assertEqual(p,prior)
        self.assertEqual([r['en'] for r in report['cells']],['S','L','P','FL','AA','G','AT','DF'])


if __name__=='__main__':unittest.main()
