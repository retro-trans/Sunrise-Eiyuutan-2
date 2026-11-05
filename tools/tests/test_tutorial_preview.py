import struct,unittest
from unittest.mock import patch
from test_binary import Cpu
from elf import Elf,PATH,ROOT
from build import inputs
import encyclopedia,tutorial_preview as preview


class TutorialPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.elf=Elf(PATH.read_bytes())

    def run_request(self,cpu,args):
        for reg,value in zip(('a0','a1','a2','a3'),args):cpu.reg(reg,value)
        cpu.reg('ra',0xffff0000);cpu.reg('sp',0x1800000);cpu.reg('gp',0x23f570)
        seen=[]
        cpu.run(preview.BASE,calls={preview.NATIVE:lambda c:seen.append(tuple(c.reg(r) for r in ('a0','a1','a2','a3')))},max_steps=500)
        self.assertEqual(cpu.reg('sp'),0x1800000);self.assertEqual(cpu.reg('gp'),0x23f570)
        return seen

    def make_cpu(self,profile):
        c=Cpu();c.put(preview.BASE,preview.payload(self.elf,profile));return c

    def test_exact_requests_once_with_native_arguments_and_return_preserved(self):
        for profile,requests in preview.PROFILES.items():
            cpu=self.make_cpu(profile)
            for n,(source,target) in enumerate(requests,1):
                args=(preview.FILE,preview.MEMBER,source,0x12345678)
                self.assertEqual(self.run_request(cpu,args),[(preview.FILE,preview.MEMBER,target,0x12345678)])
                self.assertEqual(struct.unpack('<4I',cpu.get(preview.MAIL+32+(n-1)*16,16)),(source,target,0xffff0000,n))
                self.assertEqual(self.run_request(cpu,args),[args])
                state=preview.telemetry(cpu.get(preview.MAIL,64),profile)
                self.assertEqual(state['redirects'],n)
            self.assertEqual(struct.unpack('<I',cpu.get(preview.MAIL+12,4))[0],len(requests))

    def test_other_files_members_rows_and_corrupt_telemetry_fall_back(self):
        for args in [(4951,10472,0,3),(4950,10473,0,4),(4950,10472,1,5),(4950,10472,33,6),(4950,10472,0xffffffff,7)]:
            c=self.make_cpu('missing');self.assertEqual(self.run_request(c,args),[args]);self.assertEqual(c.get(preview.MAIL+8,8),bytes(8))
        for offset,value in [(0,0),(4,99),(8,0xffffffff)]:
            c=self.make_cpu('missing');c.put(preview.MAIL+offset,struct.pack('<I',value))
            args=(4950,10472,0,3);self.assertEqual(self.run_request(c,args),[args])

    def test_source_and_reservation_guards(self):
        with self.assertRaises(ValueError):preview.payload(self.elf,'all')
        with patch.object(encyclopedia,'END',preview.BASE+1):
            with self.assertRaisesRegex(ValueError,'reserved data'):preview.payload(self.elf,'missing')
        original=self.elf.at
        with patch.object(self.elf,'at',side_effect=lambda a,n:bytes(n) if a==preview.HOOK else original(a,n)):
            with self.assertRaisesRegex(ValueError,'bridge'):preview.payload(self.elf,'missing')

    def test_default_has_no_preview_and_debug_packs_match_current_standard(self):
        normal,packs,info=inputs();f=ROOT/'work/output/v0.1.72'
        self.assertEqual(Elf(normal).at(preview.HOOK,8),preview.EXPECTED)
        for pn in (23,4905,4949,4973):self.assertEqual(packs[pn],(f/f'{pn:05d}.pack').read_bytes())
        debug,dp,di=inputs(tutorial_preview_request='missing');self.assertEqual(packs,dp)
        self.assertIsNone(info['tutorial_preview']);self.assertEqual(di['tutorial_preview'],'missing')
        elf=Elf(debug);self.assertEqual(elf.at(preview.BASE,preview.END-preview.BASE),preview.payload(self.elf,'missing'))
        self.assertEqual(elf.at(preview.HOOK,8),preview.pack([preview.j(preview.BASE),0]))
        self.assertEqual(elf.at(preview.NATIVE,76),self.elf.at(preview.NATIVE,76))
        with self.assertRaises(ValueError):inputs(preview_request=('pilot',0),tutorial_preview_request='missing')
        with self.assertRaises(ValueError):inputs(enable_vwf=False,tutorial_preview_request='row1')

    def test_telemetry_rejects_corrupt_or_unproven_records(self):
        cpu=self.make_cpu('missing');self.run_request(cpu,(4950,10472,0,7))
        good=cpu.get(preview.MAIL,64);self.assertEqual(preview.telemetry(good,'missing')['records'][0]['target_row'],1)
        for offset,value in [(0,0),(4,99),(8,9),(12,2),(16,0),(32,33),(36,2),(44,2)]:
            bad=bytearray(good);struct.pack_into('<I',bad,offset,value)
            with self.assertRaises(ValueError):preview.telemetry(bad,'missing')


if __name__=='__main__':unittest.main()
