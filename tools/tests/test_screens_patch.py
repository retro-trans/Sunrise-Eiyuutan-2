"""Native address/choice/retention checks for the focused town/save patch."""
import json,struct,unittest
import screens_patch as b
from elf import ROOT,PATH,Elf
from extract import pack_members
from textcodec import parse_table,controls,decode
from message_pages import pages
from test_binary import Cpu

class ScreensTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data,cls.packs,cls.overlays,cls.report=b.inputs();cls.elf=Elf(cls.data)
        cls.before=Elf((ROOT/'work/output/v0.2.4/SLPS_250.70').read_bytes())
        cls.addresses={k:int(v,16) for k,v in cls.report['addresses'].items()}

    def test_all_native_address_pairs_and_fixed_copies(self):
        for r in b.language()['references']:
            va=self.addresses[str(r['target'])]
            if r['kind']=='pointer':self.assertEqual(int.from_bytes(self.elf.at(r['site'],4),'little'),va);continue
            # Execute emitted high/low instructions, including LD consumers
            # whose native byte-copy counts do not follow strlen.
            c=Cpu();c.put(0x1000,self.elf.at(r['lui'],4)+self.elf.at(r['site'],4)+struct.pack('<2I',0x03E00008,0))
            c.put(va,self.elf.at(va,32));c.reg('ra',0xFFFF0000);c.run(0x1000)
            rt=(r['word']>>16)&31
            self.assertEqual(c.r[rt],int.from_bytes(self.elf.at(va,8),'little') if r['word']>>26==0x37 else va)
        for target,n in ((0x224CD8,13),(0x224CE8,19),(0x224D00,19)):
            r=next(x for x in b.language()['rows'] if x['va']==target)
            copied=self.elf.at(self.addresses[str(target)],n)
            self.assertIn(0,copied);self.assertEqual(copied.split(b'\0')[0].decode('cp932'),r['en'])

    def test_empty_slot_branch_uses_its_own_delay_slot_lui(self):
        # Execute actual empty-slot branch through its delay slot. A textual
        # nearest-LUI scan picks15036C, which is on the nonempty path instead.
        c=Cpu();c.put(0x1502B4,self.elf.at(0x1502B4,0xF8));c.put(0x1503A8,struct.pack('<2I',0x03E00008,0))
        c.reg('s0',0x5000);c.put(0x5000,b'\1');c.reg('ra',0xFFFF0000);c.run(0x1502B4)
        self.assertEqual(c.reg('a1'),self.addresses[str(0x224CC8)])
        self.assertEqual(self.elf.at(0x15036C,4),self.before.at(0x15036C,4))
        self.assertEqual(self.elf.at(0x150374,4),self.before.at(0x150374,4))

    def test_source_native_help_calls_controls_and_choices_preserved(self):
        def member(pack):
            m=next(x for x in pack_members(pack) if x['id']==1233)
            return parse_table(pack[m['offset']:m['offset']+m['size']])
        src=member((ROOT/'work/source/afs/RESOURCE/00023.bin').read_bytes());new=member(self.packs[23])
        self.assertEqual(len(new),23)
        for old,row in zip(src,new):
            self.assertEqual(controls(decode(old)),controls(decode(row)))
            sig=lambda p:tuple(p[k] for k in ('flags','speaker','voice','voice_parameter','function','arguments'))
            self.assertEqual([sig(p) for p in pages(old)],[sig(p) for p in pages(row)])
        self.assertIn('Save your current progress?\nYes\nNo',decode(new[16]))
        self.assertIn('(Items with a minimum required stock',decode(new[20]).replace('\n',' '))
        # All other pack members, including the proportional font, retained.
        def members(p):return {m['id']:p[m['offset']:m['offset']+m['size']] for m in pack_members(p)}
        old=members((ROOT/'work/output/v0.2.4/00023.pack').read_bytes());actual=members(self.packs[23])
        self.assertEqual({k:v for k,v in old.items() if k!=1233},{k:v for k,v in actual.items() if k!=1233})

    def test_overlay_changes_are_only_reviewed_pointer_words(self):
        for n in (29,35,39,43,53,60):
            src=(ROOT/f'work/source/afs/EVEMAP/{n:05d}.bin').read_bytes();new=self.overlays[n]
            self.assertEqual(len(src),len(new));changed=[]
            for pos in range(0,len(src)-3,4):
                if src[pos:pos+4]!=new[pos:pos+4]:
                    changed.append(pos);self.assertIn(int.from_bytes(new[pos:pos+4],'little'),self.addresses.values())
            self.assertEqual(changed,[0x468,0x474,0x480,0x48C,0x498,0x4A4,0x4B0,0x4BC] if n in (29,35,60) else [0x4B0] if n==39 else [0x4BC])

    def test_retained_segments_except_guarded_words(self):
        changed={int(k,16) for k in self.report['patched_words']}
        for seg in self.before.segments:
            if seg[0]!=1:continue
            va,size=seg[2],seg[4];expected=self.before.at(va,size);actual=bytearray(self.elf.at(va,size))
            for p in changed:
                if va<=p<va+size:actual[p-va:p-va+4]=expected[p-va:p-va+4]
            self.assertEqual(bytes(actual),expected)
        for n,p in self.packs.items():
            if n!=23:self.assertEqual(p,(ROOT/f'work/output/v0.2.4/{n:05d}.pack').read_bytes())
        sizeva=self.elf.symbol('_pacfileA')['va']+23*8+4
        self.assertEqual(int.from_bytes(self.elf.at(sizeva,4),'little'),len(self.packs[23]))

if __name__=='__main__':unittest.main()
