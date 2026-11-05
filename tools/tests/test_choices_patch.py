"""Protect separate Yes/No copies and observed frame-edge padding."""
import struct,unittest
import choices_patch as b
from elf import ROOT,Elf
from test_binary import Cpu

class ChoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base,cls.packs,cls.overlays,_=b.prior.inputs();cls.data,cls.report=b.patch(cls.base);cls.elf=Elf(cls.data)
        cls.addr={int(k):int(v,16) for k,v in cls.report['addresses'].items()}

    def test_distinct_choice_consumers_execute_new_addresses(self):
        for r in b.language()['references']:
            target=self.addr[r['target']]
            if r['kind']=='pointer':self.assertEqual(int.from_bytes(self.elf.at(r['site'],4),'little'),target);continue
            c=Cpu();c.put(0x1000,self.elf.at(r['lui'],4)+self.elf.at(r['site'],4)+struct.pack('<2I',0x03E00008,0));c.reg('ra',0xFFFF0000);c.run(0x1000)
            self.assertEqual(c.reg('a1'),target)
        self.assertEqual([self.elf.at(self.addr[x],8).split(b'\0')[0] for x in (0x237C60,0x237C58,0x237DC8,0x237DD0)],[b'Yes',b'No',b' Yes',b' No'])

    def test_padding_preserves_words_and_date_placeholder_order(self):
        for target in b.language()['padded_confirmations']:
            row=next(r for r in b.prior.language()['rows'] if r['va']==target)
            text=self.elf.at(self.addr[target],128).split(b'\0')[0].decode('cp932')
            self.assertEqual(text.split(),row['en'].split());self.assertTrue(all(line.startswith(' ') for line in text.split('\n')))
        fmt=self.elf.at(self.addr[0x224C70],128).split(b'\0')[0].decode('cp932')
        self.assertIn('2026/11/ 4 11:07:08',fmt%(2026,11,4,11,7,8));self.assertLess(len((fmt%(2026,11,4,11,7,8)).encode('cp932')),64)

    def test_all_other_loaded_bytes_retained_and_repeated_patch_refused(self):
        before=Elf(self.base);changed={int(k,16) for k in self.report['patched_words']}
        for seg in before.segments:
            if seg[0]!=1:continue
            va,size=seg[2],seg[4];old=before.at(va,size);new=bytearray(self.elf.at(va,size))
            for a in changed:
                if va<=a<va+size:new[a-va:a-va+4]=old[a-va:a-va+4]
            self.assertEqual(bytes(new),old)
        with self.assertRaises(ValueError):b.patch(self.data)

if __name__=='__main__':unittest.main()
