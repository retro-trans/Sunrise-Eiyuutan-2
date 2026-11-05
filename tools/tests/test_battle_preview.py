import copy,struct,unittest
from unittest.mock import patch
from test_binary import Cpu
from elf import Elf,PATH
from build import inputs
import battle_preview as preview


class BattlePreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.elf=Elf(PATH.read_bytes())

    def cpu(self,profile,first=0,count=80):
        self.first,self.count=first,count
        cpu=Cpu();cpu.put(preview.BASE,preview.payload(self.elf,profile,first,count));return cpu

    def request(self,cpu,args,inspect_progress=False):
        for r,v in zip(('a0','a1','a2','a3'),args):cpu.reg(r,v)
        cpu.reg('sp',0x1800000);cpu.reg('ra',0xffff0000);cpu.reg('gp',0x23f570)
        for i in range(3):cpu.reg('s'+str(i),0x12345678+i)
        seen=[]
        def call(c):
            seen.append(tuple(c.reg(r) for r in ('a0','a1','a2','a3')))
            if inspect_progress:
                state=preview.telemetry(c.get(preview.MAIL,64),self.profile,self.first,self.count)
                self.assertEqual((state['state'],state['current_row'],state['completed_rows']),(1,self.first+len(seen)-1,len(seen)-1))
            # Original native ABI may overwrite every argument and temporary.
            for r in ('a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7','t8','t9'):c.reg(r,0xdeadbeef)
            c.reg('v0',0x1234)
        cpu.run(preview.BASE,calls={preview.NATIVE:call},max_steps=10000)
        self.assertEqual(cpu.reg('sp'),0x1800000);self.assertEqual(cpu.reg('gp'),0x23f570)
        for i in range(3):self.assertEqual(cpu.reg('s'+str(i)),0x12345678+i)
        self.assertEqual(cpu.reg('v0'),0x1234)
        return seen

    def test_both_physical_profiles_run80_native_calls_once_and_restore_callee_state(self):
        for profile,(pid,file,member,table) in preview.PROFILES.items():
            self.profile=profile;cpu=self.cpu(profile)
            self.assertEqual(self.request(cpu,preview.SOURCE+(0xabcdef,),True),[(file,member,i,0xabcdef) for i in range(80)])
            state=preview.telemetry(cpu.get(preview.MAIL,64),profile)
            self.assertEqual((state['state'],state['completed_rows'],state['requests']),(2,80,1))
            args=preview.SOURCE+(3,);self.assertEqual(self.request(cpu,args),[args])

    def test_unmatched_or_corrupt_guard_falls_through_without_loop(self):
        for args in [(4951,10472,0,3),(4950,10473,0,4),(4950,10472,1,5)]:
            cpu=self.cpu('canonical');self.assertEqual(self.request(cpu,args),[args]);self.assertEqual(cpu.get(preview.MAIL+8,4),bytes(4))
        for off,value in [(0,0),(4,99),(8,1),(8,2),(44,1),(48,81)]:
            cpu=self.cpu('canonical');cpu.put(preview.MAIL+off,struct.pack('<I',value));args=preview.SOURCE+(9,)
            self.assertEqual(self.request(cpu,args),[args])

    def test_later_and_short_ranges_use_absolute_rows_relative_progress_and_one_use(self):
        for profile,(pid,file,member,table) in preview.PROFILES.items():
            self.profile=profile
            for first,count in ((80,80),(160,80),(240,80),(320,29),(350,50),(400,80),(195,10),(114,46),(6518,1)):
                with self.subTest(profile=profile,first=first,count=count):
                    cpu=self.cpu(profile,first,count)
                    self.assertEqual(self.request(cpu,preview.SOURCE+(123,),True),[(file,member,i,123) for i in range(first,first+count)])
                    state=preview.telemetry(cpu.get(preview.MAIL,64),profile,first,count)
                    self.assertEqual((state['state'],state['current_row'],state['completed_rows'],state['requests']),(2,first+count-1,count,1))
                    with self.assertRaises(ValueError):preview.telemetry(cpu.get(preview.MAIL,64),profile)
                    args=preview.SOURCE+(8,);self.assertEqual(self.request(cpu,args),[args])

    def test_range_bounds_language_gate_and_closed74_payload_compatibility(self):
        for first,count in ((-1,80),(0,0),(0,81),(6519,1),(6518,2),(True,1),(80,False),(1.5,2)):
            with self.subTest(first=first,count=count),self.assertRaises(ValueError):preview.payload(self.elf,'canonical',first,count)
        exports={t:dict(rows=[dict(id=i,review=dict(accuracy='independent-reviewed',editorial='self-reviewed',proofread='self-reviewed')) for i in range(80,160)]) for t in preview.battle_bank.TABLES}
        preview.require_translations(exports,80,80)
        exports[preview.battle_bank.ALIAS]['rows'][33]['review']['accuracy']='pending'
        with self.assertRaises(ValueError):preview.require_translations(exports,80,80)
        with self.assertRaises(ValueError):inputs(battle_preview_first=80)
        closed=Elf((preview.battle_bank.ROOT/'work/output/v0.1.74/SLPS_250.70').read_bytes())
        self.assertEqual(closed.at(preview.BASE,preview.END-preview.BASE),preview.payload(self.elf,'canonical'))

    def test_unresolved_gap_rejects_whole_slice_but_accepts_reviewed_subranges(self):
        normal,packs,info=inputs()
        import json
        exports={p.stem[:-3]:json.loads(p.read_text()) for p in (preview.battle_bank.ROOT/'work/translation/en/dat').glob('*.en.json')}
        preview.require_translations(exports,320,29)
        preview.require_translations(exports,350,50)
        preview.require_translations(exports,400,80)
        preview.require_translations(exports,selected_rows=preview.parse_rows('480-502,504-524,526-559'))
        with self.assertRaises(ValueError):preview.require_translations(exports,480,80)
        with self.assertRaises(ValueError):preview.require_translations(exports,selected_rows=[503,525])
        with self.assertRaises(ValueError):preview.require_translations(exports,320,80)
        with self.assertRaises(ValueError):inputs(battle_preview_request='canonical',battle_preview_first=320,battle_preview_count=80)

    def test_telemetry_rejects_invalid_limits_progress_and_request_provenance(self):
        cpu=self.cpu('alias');self.request(cpu,preview.SOURCE+(7,));good=cpu.get(preview.MAIL,64)
        for off,value in [(0,0),(4,1),(8,9),(12,80),(16,79),(24,0),(28,0),(32,1),(36,23),(40,10512),(44,1),(48,0),(52,2),(56,1)]:
            bad=bytearray(good);struct.pack_into('<I',bad,off,value)
            with self.subTest(offset=off),self.assertRaises(ValueError):preview.telemetry(bad,'alias')

    def test_mode_reservation_review_guards_and_current_pack_equivalence(self):
        normal,np,ni=inputs();debug,dp,di=inputs(battle_preview_request='canonical')
        self.assertEqual(np,dp);self.assertIsNone(ni['battle_preview']);self.assertEqual(di['battle_preview'],'canonical')
        elf=Elf(debug);self.assertEqual(elf.at(preview.BASE,preview.END-preview.BASE),preview.payload(self.elf,'canonical'))
        self.assertEqual(elf.at(preview.NATIVE,76),self.elf.at(preview.NATIVE,76))
        for args in [dict(preview_request=('pilot',0),battle_preview_request='canonical'),dict(tutorial_preview_request='missing',battle_preview_request='alias'),dict(enable_vwf=False,battle_preview_request='canonical')]:
            with self.assertRaises(ValueError):inputs(**args)
        with self.assertRaises(ValueError):preview.require_translations({})
        with self.assertRaises(ValueError):preview.payload(self.elf,'all')
        with patch.object(preview.encyclopedia,'END',preview.BASE+1):
            with self.assertRaises(ValueError):preview.payload(self.elf,'canonical')

    def test_explicit_rows_execute_only_selected_native_calls_with_relative_progress(self):
        selections=[preview.parse_rows('480-502,504-524,526-559'),[6518],list(range(0,160,2))]
        for profile,(pid,file,member,table) in preview.PROFILES.items():
            for ids in selections:
                with self.subTest(profile=profile,rows=len(ids)):
                    cpu=Cpu();cpu.put(preview.BASE,preview.payload(self.elf,profile,selected_rows=ids));seen=[]
                    cpu.reg('sp',0x1800000);cpu.reg('ra',0xffff0000);cpu.reg('gp',0x23f570)
                    for i in range(3):cpu.reg('s'+str(i),0x12345678+i)
                    for r,v in zip(('a0','a1','a2','a3'),preview.SOURCE+(0xabcdef,)):cpu.reg(r,v)
                    def native(c):
                        seen.append(tuple(c.reg(r) for r in ('a0','a1','a2','a3')))
                        state=preview.telemetry(c.get(preview.MAIL,64),profile,selected_rows=ids)
                        self.assertEqual((state['state'],state['current_row'],state['completed_rows']),(1,ids[len(seen)-1],len(seen)-1))
                        for r in ('a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7','t8','t9'):c.reg(r,0xdeadbeef)
                        c.reg('v0',0x1234)
                    cpu.run(preview.BASE,calls={preview.NATIVE:native},max_steps=10000)
                    self.assertEqual(seen,[(file,member,i,0xabcdef) for i in ids])
                    self.assertEqual((cpu.reg('sp'),cpu.reg('gp'),cpu.reg('v0')),(0x1800000,0x23f570,0x1234))
                    for i in range(3):self.assertEqual(cpu.reg('s'+str(i)),0x12345678+i)
                    state=preview.telemetry(cpu.get(preview.MAIL,64),profile,ids[0],len(ids),ids)
                    self.assertEqual((state['state'],state['current_row'],state['completed_rows'],state['requests']),(2,ids[-1],len(ids),1))
                    self.profile=profile;self.assertEqual(self.request(cpu,preview.SOURCE+(9,)),[preview.SOURCE+(9,)])

    def test_explicit_selection_rejects_bad_ids_conflicts_and_unreviewed_physical_rows(self):
        for ids in ([],[True],[1.5],[-1],[6519],[3,2],[2,2],list(range(81)),'1,3'):
            with self.subTest(ids=ids),self.assertRaises(ValueError):preview.payload(self.elf,'canonical',selected_rows=ids)
        for value in ('','1,','3-2','0-6518','6519','1,,2','1-2,2','1 2','1,-2'):
            with self.subTest(text=value),self.assertRaises(ValueError):preview.parse_rows(value)
        with self.assertRaises(ValueError):preview.payload(self.elf,'canonical',480,80,[480,482])
        with self.assertRaises(ValueError):inputs(battle_preview_rows=[0,2])
        ids=[480,502,504,524,526,559]
        exports={t:dict(rows=[dict(id=i,review=dict(accuracy='independent-reviewed',editorial='self-reviewed',proofread='self-reviewed')) for i in ids]) for t in preview.battle_bank.TABLES}
        preview.require_translations(exports,selected_rows=ids)
        with self.assertRaises(ValueError):preview.require_translations(exports,selected_rows=[480,503])
        for bad in ('pending','failed',None):
            exports[preview.battle_bank.ALIAS]['rows'][2]['review']['proofread']=bad
            with self.subTest(status=bad),self.assertRaises(ValueError):preview.require_translations(exports,selected_rows=ids)

    def test_explicit_header_and_telemetry_reject_mixed_selections_and_invalid_progress(self):
        ids=[480,502,504,524,526,559]
        for off,value in ((0,preview.MAGIC),(4,2),(8,1),(44,479),(48,80),(56,0),(60,0)):
            cpu=Cpu();cpu.put(preview.BASE,preview.payload(self.elf,'canonical',selected_rows=ids));cpu.put(preview.MAIL+off,struct.pack('<I',value))
            self.assertEqual(self.request(cpu,preview.SOURCE+(7,)),[preview.SOURCE+(7,)])
        cpu=Cpu();cpu.put(preview.BASE,preview.payload(self.elf,'canonical',selected_rows=ids));self.request(cpu,preview.SOURCE+(7,));good=cpu.get(preview.MAIL,64)
        for off,value in ((12,503),(16,5),(24,0),(52,2),(56,0),(60,0)):
            bad=bytearray(good);struct.pack_into('<I',bad,off,value)
            with self.subTest(offset=off),self.assertRaises(ValueError):preview.telemetry(bad,'canonical',selected_rows=ids)
        with self.assertRaises(ValueError):preview.telemetry(good,'canonical')
        with self.assertRaises(ValueError):preview.telemetry(good,'canonical',selected_rows=[480,501,504,524,526,559])

    def test_explicit_build_metadata_pack_identity_and_closed_range_payload_compatibility(self):
        ids=list(range(320,349))+list(range(350,400))
        normal,np,ni=inputs();debug,dp,di=inputs(battle_preview_request='canonical',battle_preview_rows=ids)
        self.assertEqual(np,dp);self.assertIsNone(ni['battle_preview_rows'])
        self.assertEqual((di['battle_preview_first'],di['battle_preview_count'],di['battle_preview_rows']),(320,79,ids))
        built=Elf(debug);self.assertEqual(built.at(preview.BASE,preview.END-preview.BASE),preview.payload(self.elf,'canonical',320,79,ids))
        closed=Elf((preview.battle_bank.ROOT/'work/output/v0.1.94/SLPS_250.70').read_bytes())
        self.assertEqual(closed.at(preview.BASE,preview.END-preview.BASE),preview.payload(self.elf,'canonical',400,80))
        oldnormal=Elf((preview.battle_bank.ROOT/'work/output/v0.1.96/SLPS_250.70').read_bytes());current=Elf(normal)
        for va,n in ((preview.HOOK,8),(0x9a4000,512),(0x9aa000,552),(0x9aa300,660),(0x9aa800,44),(0x9aaa00,108)):
            self.assertEqual(current.at(va,n),oldnormal.at(va,n))


if __name__=='__main__':unittest.main()
