"""Protect native Options choice ordering, address construction, fit and retention."""
import json,struct,unittest
from elf import ROOT,Elf
from test_binary import Cpu
import options_patch as b

class OptionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base,cls.packs,cls.overlays,_=b.prior.inputs();cls.data,cls.report=b.patch(cls.base);cls.e=Elf(cls.data)
        cls.addr={int(k):int(v,16) for k,v in cls.report['addresses'].items()}

    def test_native_tables_and_heading_address_execution(self):
        expected=['Message Speed','BGM Volume','SE Volume','Voice Volume','B.E.S Volume']
        for table,labels in ((0x222010,expected),(0x222080,['Fast','Slightly Fast','Normal','Slightly Slow','Slow'])):
            ptrs=struct.unpack('<5I',self.e.at(table,20))
            self.assertEqual([self.e.at(p,32).split(b'\0')[0].decode('ascii') for p in ptrs],labels)
        r=next(r for r in b.language()['references'] if r['kind']=='code');c=Cpu()
        c.put(0x1000,self.e.at(r['lui'],4)+self.e.at(r['site'],4)+struct.pack('<2I',0x03E00008,0));c.reg('ra',0xFFFF0000);c.run(0x1000)
        self.assertEqual(c.reg('a0'),self.addr[0x222028])
        self.assertEqual(int.from_bytes(self.e.at(0x237CC4,4),'little'),self.addr[0x222558])

    def test_popup_geometry_and_measured_width(self):
        widths=json.loads((ROOT/'work/output/v0.2.7/build_info.json').read_text('utf8'))['font_widths']
        for va,(old,new) in b.GEOMETRY.items():self.assertEqual(int.from_bytes(self.e.at(va,4),'little'),new)
        self.assertEqual(224+192//2,320)
        for r in b.language()['rows']:
            limit=192 if r['va'] in (0x222060,0x222070,0x237BD0,0x237BD8,0x237BE0) else 196
            self.assertLess(sum(widths[ord(c)]+2 for c in r['en']),limit-8,r['en'])

    def test_retained_exit_and_all_other_loaded_bytes(self):
        before=Elf(self.base);changed={int(k,16) for k in self.report['patched_words']}
        for seg in before.segments:
            if seg[0]!=1:continue
            va,size=seg[2],seg[4];old=before.at(va,size);new=bytearray(self.e.at(va,size))
            for a in changed:
                if va<=a<va+size:new[a-va:a-va+4]=old[a-va:a-va+4]
            self.assertEqual(bytes(new),old)
        # The caller's existing relocated exit question remains untouched.
        self.assertEqual(self.e.at(0x1029B0,4),before.at(0x1029B0,4));self.assertEqual(self.e.at(0x102A18,4),before.at(0x102A18,4))
        with self.assertRaises(ValueError):b.patch(self.data)

if __name__=='__main__':unittest.main()
