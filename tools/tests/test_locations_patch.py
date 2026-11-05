"""Exercise native indexed name getters and retain every unrelated loaded byte."""
import json,unittest
from elf import ROOT,Elf
from test_binary import Cpu
import locations_patch as b

class LocationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base,cls.packs,cls.previous,_=b.prior.inputs();cls.data,cls.report=b.patch(cls.base);cls.e=Elf(cls.data)
        cls.overlays,cls.edits=b.patch_overlays(cls.previous,cls.report['addresses']);cls.d=b.language()

    def test_native_all_town_and_continent_getters(self):
        for r in self.d['tables']:
            c=Cpu();table=0x1C10F8 if r['table']=='_townname' else 0x1C08F0
            start,size=(0x12FDE8,28) if r['table']=='_townname' else (0x12ED40,60)
            c.put(start,self.e.at(start,size));c.put(table,self.e.at(table,104 if table==0x1C10F8 else 36))
            c.reg('a0',r['index']+1);c.reg('sp',0x6000);c.reg('s0',0x12345678);c.reg('ra',0xFFFF0000)
            # Bound the unrelated validity-helper call; execute the native
            # index arithmetic, load, saved registers and return delay slot.
            c.run(start,calls={0x12ED28:lambda c:c.reg('v0',int(0<c.reg('a0')<10))})
            self.assertEqual(self.e.at(c.reg('v0'),100).split(b'\0')[0].decode('ascii'),r['en'])
            self.assertEqual(c.reg('s0'),0x12345678)

    def test_all_local_and_map_consumers_resolve_complete_labels(self):
        for r in self.d['overlays']:
            out=self.overlays[r['member']];address=int(self.report['addresses'][r['id']],16)
            self.assertEqual(self.e.at(address,100).split(b'\0')[0].decode('ascii'),r['en'])
            for site in r['sites']:self.assertEqual(int.from_bytes(out[site:site+4],'little'),address)
            for ref in r['code']:
                c=Cpu();c.put(0x9E0000+ref['lui'],out[ref['lui']:ref['site']+4]);c.run(0x9E0000+ref['lui'],stop=0x9E0000+ref['site']+4)
                self.assertEqual(c.reg('a1'),address)
        # The kingdom/capital and venue are separate native selections.
        for n,city,capital in ((46,'A','Laas Wau'),(47,'Ku','Kemi'),(48,'Lau','Tatara'),(49,'Na','Uroporos'),(53,'Tokio','G-Island City')):
            out=self.overlays[n]
            for site,text in ((0x468,city),(0x474,capital)):
                address=int.from_bytes(out[site:site+4],'little');self.assertEqual(self.e.at(address,80).split(b'\0')[0].decode('ascii'),text)

    def test_unrelated_loaded_bytes_ids_availability_and_assets_preserved(self):
        old=Elf(self.base);changed={int(k,16) for k in self.report['patched_words']}
        for seg in old.segments:
            if seg[0]!=1:continue
            va,size=seg[2],seg[4];before=old.at(va,size);after=bytearray(self.e.at(va,size))
            for p in changed:
                if va<=p<va+size:after[p-va:p-va+4]=before[p-va:p-va+4]
            self.assertEqual(bytes(after),before)
        for n,out in self.overlays.items():
            before=self.previous.get(n,(ROOT/f'work/source/afs/EVEMAP/{n:05d}.bin').read_bytes());after=bytearray(out)
            for p in self.edits.get(str(n),{}):
                site=int(p,16);after[site:site+4]=before[site:site+4]
            self.assertEqual(bytes(after),before);self.assertEqual(len(out),131072)
        with self.assertRaises(ValueError):b.patch(self.data)

    def test_names_fit_full_width_headers_and_dynamic_picker(self):
        widths=json.loads((ROOT/'work/output/v0.2.10/build_info.json').read_text('utf8'))['font_widths']
        for r in self.d['tables']+self.d['overlays']:
            self.assertLess(sum(widths[ord(c)]+2 for c in r['en']),544,r['en'])
        # Native town picker already measures every current label to size it;
        # its instructions and availability are covered by byte retention above.
        self.assertEqual(len(self.d['tables']),35);self.assertEqual(len(self.d['overlays']),262)

if __name__=='__main__':unittest.main()
