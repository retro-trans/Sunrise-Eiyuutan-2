"""Execute the real native memory-card centering function and its new branch."""
import json,struct,unittest
from elf import ROOT,Elf
from test_binary import Cpu
import mc_font_patch as b

class MCFontTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base,_,_,_=b.prior.inputs();cls.data=b.patch(cls.base);cls.e=Elf(cls.data)
        cls.widths=bytes(json.loads((ROOT/'work/output/v0.2.6/build_info.json').read_text('utf8'))['font_widths'])

    def invoke(self,text,data):
        e=Elf(data);raw=text.encode('cp932');c=Cpu();c.put(0x1523B8,e.at(0x1523B8,0xC0));c.put(b.BASE,b.code());c.put(0x9A4000,self.widths)
        c.put(0x7000,raw+b'\0');c.put(0x6020,struct.pack('<I',512));c.reg('a0',0x6000);c.reg('a1',0x7000);c.reg('a2',12);c.reg('a3',0);c.reg('sp',0x9000);c.reg('ra',0xFFFF0000);c.reg('s1',0x12345678)
        result={}
        def strlen(m):m.reg('v0',len(raw))
        def draw(m):result.update(x=m.reg('a2'),y=m.reg('a3'))
        c.run(0x1523B8,calls={0x19F7D8:strlen,0x110E98:draw},max_steps=4000)
        self.assertEqual(c.reg('s1'),0x12345678);self.assertEqual(result['y'],12)
        return result['x']

    def test_real_ascii_center_uses_measured_font_not_fifteen_per_byte(self):
        for text in ('Last Updated    2026/11/ 4 11:07:08','Do you want to cancel saving?',' Yes',' No','IIII WWWW'):
            width=sum(self.widths[ord(c)]+2 for c in text)
            self.assertEqual(self.invoke(text,self.data),(512-width)//2)
            self.assertNotEqual(self.invoke(text,self.base),(512-width)//2)

    def test_wide_branch_and_all_previous_loaded_bytes_retained(self):
        text='\u30af\u30e9\u30a6\u30c9\u30b7\u30c6\u30a3'
        self.assertEqual(self.invoke(text,self.data),self.invoke(text,self.base))
        old=Elf(self.base)
        for s in old.segments:
            if s[0]!=1:continue
            va,size=s[2],s[4];expected=old.at(va,size);actual=bytearray(self.e.at(va,size))
            if va<=b.HOOK<va+size:actual[b.HOOK-va:b.HOOK-va+8]=expected[b.HOOK-va:b.HOOK-va+8]
            self.assertEqual(bytes(actual),expected)
        with self.assertRaises(ValueError):b.patch(self.data)

if __name__=='__main__':unittest.main()
