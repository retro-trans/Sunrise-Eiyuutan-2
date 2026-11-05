"""Execute the actual dynamic ship-header path and preserve deck dispatch."""
import json,struct,unittest
from elf import ROOT,Elf
from test_binary import Cpu
import deck_patch as b

class DeckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base,cls.packs,cls.overlays,_=b.prior.inputs();cls.data,cls.report=b.patch(cls.base);cls.e=Elf(cls.data)
        cls.addr={int(k):int(v,16) for k,v in cls.report['addresses'].items()}

    def test_real_dynamic_ship_header_getter_uses_astante(self):
        c=Cpu()
        for va,n in ((0x12F968,32),(0x156398,20),(0x1563F0,32),(0x1E6EE0,128)):
            c.put(va,self.e.at(va,n))
        c.reg('sp',0x7000);c.reg('ra',0xFFFF0000);seen={}
        def player(m):m.reg('v0',1)
        def mesval(m):seen.update(slot=m.reg('a0'),pointer=m.reg('a1'))
        c.run(0x12F968,stop=0x12F984,calls={0x1306F8:player,0x12C620:mesval})
        self.assertEqual(seen,dict(slot=1,pointer=self.addr[0x22E7E8]))
        self.assertEqual(self.e.at(seen['pointer'],8),b'Astante\0')

    def test_sailing_branch_stack_label_and_destination_dispatch(self):
        c=Cpu();c.put(0x12FA24,self.e.at(0x12FA24,28));c.reg('a1',6);c.reg('sp',0x6000)
        c.run(0x12FA24,stop=0x12FA48)
        self.assertEqual(int.from_bytes(c.get(0x6018,4),'little'),self.addr[0x237AB8])
        self.assertEqual(self.e.at(self.addr[0x237AB8],5),b'Sail\0')
        self.assertEqual(int.from_bytes(self.e.at(0x221740,4),'little'),self.addr[0x221710])
        old=Elf(self.base);self.assertEqual(self.e.at(0x221750,40),old.at(0x221750,40))
        self.assertEqual(self.e.at(0x12FC14,16),old.at(0x12FC14,16))
        widths=json.loads((ROOT/'work/output/v0.2.8/build_info.json').read_text('utf8'))['font_widths']
        self.assertEqual(sum(widths[ord(c)]+1 for c in 'Select Destination'),198)
        self.assertLess(198,216-8)

    def test_ship_metadata_and_all_previous_loaded_bytes_retained(self):
        before=Elf(self.base);changed={int(k,16) for k in self.report['patched_words']}
        for seg in before.segments:
            if seg[0]!=1:continue
            va,size=seg[2],seg[4];old=before.at(va,size);new=bytearray(self.e.at(va,size))
            for a in changed:
                if va<=a<va+size:new[a-va:a-va+4]=old[a-va:a-va+4]
            self.assertEqual(bytes(new),old)
        self.assertEqual(self.e.at(0x1E6F20,4),before.at(0x1E6F20,4)) # Long description unchanged
        self.assertEqual(self.e.at(0x1E6F2C,52),before.at(0x1E6F2C,52)) # Stats/flags unchanged
        with self.assertRaises(ValueError):b.patch(self.data)

if __name__=='__main__':unittest.main()
