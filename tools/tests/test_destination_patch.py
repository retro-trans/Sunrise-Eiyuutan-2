"""Native town getter, selector argument construction and guarded Deon tables."""
import json,struct,unittest
from elf import ROOT,Elf
from test_binary import Cpu
import destination_patch as b

class DestinationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base,cls.packs,cls.previous,_=b.prior.inputs();cls.data,cls.report=b.patch(cls.base);cls.e=Elf(cls.data)
        cls.overlays,cls.edits=b.patch_overlays(cls.previous,cls.report['addresses'])
        cls.addr={k:int(v,16) for k,v in cls.report['addresses'].items()}

    def test_actual_town_getter_returns_full_names_and_preserves_other_towns(self):
        old=Elf(self.base)
        for number in range(1,27):
            c=Cpu();c.put(0x12FDE8,self.e.at(0x12FDE8,28));c.put(0x1C10F8,self.e.at(0x1C10F8,104));c.reg('a0',number);c.reg('ra',0xFFFF0000);c.run(0x12FDE8)
            if number in (1,2,3,26):
                en={1:'Cloud City',2:'Deon Town',3:'Astante Fortress Ruins',26:'Cloud City'}[number]
                self.assertEqual(self.e.at(c.reg('v0'),40).split(b'\0')[0].decode('ascii'),en)
            else:self.assertEqual(c.reg('v0'),int.from_bytes(old.at(0x1C10F8+(number-1)*4,4),'little'))

    def test_actual_selector_heading_none_and_complete_name_widths(self):
        c=Cpu();c.put(0x138D7C,self.e.at(0x138D7C,28));c.reg('sp',0x6000);c.run(0x138D7C,stop=0x138D98)
        self.assertEqual(c.reg('s5'),self.addr[str(0x237AE8)]);self.assertEqual(c.reg('a0'),self.addr[str(0x221968)])
        old=Elf(self.base)
        # Preserve actual dynamic width measurement and native selection writes.
        self.assertEqual(self.e.at(0x138D98,0x13905C-0x138D98),old.at(0x138D98,0x13905C-0x138D98))
        w=json.loads((ROOT/'work/output/v0.2.9/build_info.json').read_text('utf8'))['font_widths']
        for r in b.language()['rows']:self.assertLess(sum(w[ord(c)]+2 for c in r['en']),608)

    def test_deon_overlay_name_pointers_and_all_other_bytes_retained(self):
        for r in b.language()['overlays']:
            blob=self.overlays[r['member']]
            for site in r['sites']:self.assertEqual(int.from_bytes(blob[site:site+4],'little'),self.addr[r['id']])
            self.assertEqual(self.e.at(self.addr[r['id']],40).split(b'\0')[0].decode('ascii'),r['en'])
        self.assertEqual(self.addr['EVEMAP/00036:000004D0'],self.addr[str(0x221678)])
        self.assertEqual(self.addr['EVEMAP/00061:000009C0'],b.CLOUD_PRIOR)
        self.assertEqual(self.addr['EVEMAP/00061:00000998'],self.addr[str(0x221660)])
        for n in (36,61):
            old=(ROOT/f'work/source/afs/EVEMAP/{n:05d}.bin').read_bytes();actual=bytearray(self.overlays[n])
            for site in self.edits[str(n)]:
                p=int(site,16);actual[p:p+4]=old[p:p+4]
            self.assertEqual(bytes(actual),old);self.assertEqual(len(self.overlays[n]),131072)
        for n,blob in self.previous.items():self.assertEqual(self.overlays[n],blob)

    def test_all_previous_loaded_bytes_retained_and_repeat_refused(self):
        before=Elf(self.base);changed={int(k,16) for k in self.report['patched_words']}
        for seg in before.segments:
            if seg[0]!=1:continue
            va,size=seg[2],seg[4];old=before.at(va,size);new=bytearray(self.e.at(va,size))
            for a in changed:
                if va<=a<va+size:new[a-va:a-va+4]=old[a-va:a-va+4]
            self.assertEqual(bytes(new),old)
        with self.assertRaises(ValueError):b.patch(self.data)

if __name__=='__main__':unittest.main()
