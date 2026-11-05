import copy,json,struct,unittest
from unittest.mock import patch
from test_binary import ROOT,Cpu
from elf import Elf,PATH
from battle_bank import *
from build import inputs
from textcodec import decode,build_table
from story_layout import wrap_row
import test_message_pages as native_pages
from resource_origin import origin,HEAD,END,LOOKUP


class BattleBankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=Elf(PATH.read_bytes());cls.raw=original_tables()
        cls.draft=json.loads((ROOT/'work/translation/en/dat/00022_10512.json').read_text(encoding='utf-8'))['rows']
        cls.widths=json.loads((ROOT/'work/output/v0.1.72/build_info.json').read_text())['font_widths']

    def sample(self):
        source=dict(id=0,en='Reviewed language',source_sha256=sha(self.raw[CANONICAL][0]),review=dict(accuracy='independent-reviewed',editorial='self-reviewed',proofread='self-reviewed',rendered_fit='passed'),rendered_evidence=dict(build='0.1.72',draft_sha256=sha(b'Reviewed language'),built_row_sha256='a'*64,native_sha256='b'*64,pages=1,audit='canonical-only',build_elf_sha256='c'*64))
        exports={CANONICAL:dict(table=CANONICAL,rows=[source])}
        plan=dict(schema='exact-source-aliases-v1',aliases=[dict(source_table=CANONICAL,target_table=ALIAS,whole_table_sha256=SOURCE_SHA,rows=[dict(source_id=0,target_id=0,source_sha256=sha(self.raw[CANONICAL][0]))])])
        return exports,plan

    def test_alias_shares_language_but_never_inherits_canonical_native_evidence(self):
        exports,plan=self.sample();before=copy.deepcopy(exports)
        target=expand_aliases(exports,plan,self.raw)[ALIAS]['rows'][0]
        self.assertEqual(target['en'],exports[CANONICAL]['rows'][0]['en']);self.assertEqual(target['review']['accuracy'],'independent-reviewed')
        self.assertEqual(target['review']['rendered_fit'],'pending');self.assertNotIn('rendered_evidence',target);self.assertEqual(exports,before)
        self.assertEqual(target['alias_of'],dict(table=CANONICAL,id=0,source_sha256=sha(self.raw[CANONICAL][0])))

    def test_alias_own_physical_evidence_is_separate_and_expires_on_wording_change(self):
        exports,plan=self.sample();own=copy.deepcopy(exports[CANONICAL]['rows'][0]['rendered_evidence']);own.update(build='0.1.75',audit='alias-own-proof')
        plan['aliases'][0]['rows'][0]['rendered_evidence']=own
        result=expand_aliases(exports,plan,self.raw)[ALIAS]['rows'][0]
        self.assertEqual(result['review']['rendered_fit'],'passed');self.assertEqual(result['rendered_evidence']['audit'],'alias-own-proof')
        exports[CANONICAL]['rows'][0]['en']='Changed complete wording'
        result=expand_aliases(exports,plan,self.raw)[ALIAS]['rows'][0]
        self.assertEqual(result['review']['rendered_fit'],'pending');self.assertNotIn('rendered_evidence',result)

    def test_alias_rejects_source_drift_nonidentical_ids_duplicates_and_conflicts(self):
        for problem in ('hash','id','duplicate','missing','conflict','direction','revision','bytes'):
            exports,plan=self.sample();tables=dict(self.raw);p=plan['aliases'][0]
            if problem=='hash':p['rows'][0]['source_sha256']='0'*64
            elif problem=='id':p['rows'][0]['target_id']=1
            elif problem=='duplicate':p['rows']*=2
            elif problem=='missing':exports[CANONICAL]['rows']=[]
            elif problem=='conflict':exports[ALIAS]=dict(table=ALIAS,rows=[])
            elif problem=='direction':p['source_table'],p['target_table']=p['target_table'],p['source_table']
            elif problem=='revision':p['whole_table_sha256']='0'*64
            else:tables[ALIAS]=list(tables[ALIAS]);tables[ALIAS][0]=b'Different\0'
            with self.subTest(problem=problem),self.assertRaises(ValueError):expand_aliases(exports,plan,tables)

    def test_all1568_original_and_reflowed_english_calls_match_original_machine_code(self):
        calls=bodies=0
        for row in self.draft:
            i=row['id'];english,report=wrap_row(row['en'],self.widths,profile='battle-barks')
            validate_row(decode(self.raw[CANONICAL][i]),english);bodies+=len(report)
            self.assertTrue(all(p['lines']<=3 and p['prompt_right_px']<=504 for p in report))
            for raw in (self.raw[CANONICAL][i],encode(english)):
                for page in pages(raw):
                    self.assertEqual(page,native_pages.MessagePageTests.native(self,raw,page['start']));calls+=1
        self.assertEqual([r['id'] for r in self.draft],[i for i in range(1600) if i not in (349,503,525,635,643,644,760,774,855,873,880,945,949,992,1005,1043,1060,1089,1102,1132,1163,1195,1219,1230,1269,1305,1310,1352,1395,1450,1457,1538)])
        self.assertEqual((calls,bodies),(8298,1568))

    def test_both_physical_packs_build_exact_alias_rows_and_preserve_other_members(self):
        elf,packs,info=inputs();self.assertEqual(set(packs),{22,23,4905,4949,4971,4973})
        self.assertEqual(len(info['translated_rows']),3828);built={}
        for name in TABLES:
            pn,mid=map(int,name.split('_'));old=(ROOT/f'work/source/afs/RESOURCE/{pn:05d}.bin').read_bytes()
            for member in pack_members(packs[pn]):
                data=packs[pn][member['offset']:member['offset']+member['size']]
                original=next(m for m in pack_members(old) if m['id']==member['id'])
                if member['id']==mid:built[name]=parse_table(data)
                else:self.assertEqual(data,old[original['offset']:original['offset']+original['size']])
            self.assertEqual(built[name][1600:],self.raw[name][1600:])
            for i in (349,503,525,635,643,644,760,774,855,873,880,945,949,992,1005,1043,1060,1089,1102,1132,1163,1195,1219,1230,1269,1305,1310,1352,1395,1450,1457,1538):self.assertEqual(built[name][i],self.raw[name][i])
            oldpack=(ROOT/f'work/output/v0.1.136/{pn:05d}.pack').read_bytes()
            oldmember=next(m for m in pack_members(oldpack) if m['id']==mid)
            prior=parse_table(oldpack[oldmember['offset']:oldmember['offset']+oldmember['size']])
            self.assertEqual(built[name][:1520],prior[:1520])
        self.assertEqual(built[CANONICAL],built[ALIAS])
        for pn in (23,4905,4949,4973):self.assertEqual(packs[pn],(ROOT/f'work/output/v0.1.72/{pn:05d}.pack').read_bytes())

    def test_unprofiled_battle_controls_and_source_revision_fail(self):
        with self.assertRaises(ValueError):validate_table(b'ATMB'+bytes(20),CANONICAL)
        row=self.draft[0]['en']
        with self.assertRaises(ValueError):validate_row(decode(self.raw[CANONICAL][0]),row.replace('Here I go!!','{C:819782830400}Here I go!!'))
        function='\n{C:8195828601000000}Function\n\n{x00}'
        with self.assertRaises(ValueError):validate_row(function,function)

    def test_exact_unvoiced_sources_preserve_original_parser_calls_without_voice_cues(self):
        # This exercises the shipped parser machine code as well as the English
        # layout. Generic speaker24 alone must never grant staging permission.
        english={r['id']:r['en'] for r in self.draft};calls=0
        for i,expected_sha in UNVOICED_SOURCES.items():
            self.assertEqual(sha(self.raw[CANONICAL][i]),expected_sha)
            source=decode(self.raw[CANONICAL][i]);wrapped,layout=wrap_row(english[i],self.widths,profile='battle-barks')
            self.assertEqual(validate_row(source,wrapped),'unvoiced-source-195-204')
            self.assertEqual(len(layout),1);self.assertTrue(all(p['voice']==0 for p in layout))
            for raw in (self.raw[CANONICAL][i],encode(wrapped)):
                model=pages(raw);self.assertEqual([p['flags'] for p in model],[0,0x11,0])
                self.assertEqual(model[1]['speaker'],24)
                self.assertTrue(all(p['voice']==p['voice_parameter']==0 for p in model))
                for page in model:
                    self.assertEqual(page,native_pages.MessagePageTests.native(self,raw,page['start']));calls+=1
        self.assertEqual(calls,60)
        # Native voice startup is conditional; no runtime patch is needed.
        self.assertEqual(self.elf.at(0x12c8a4,20),bytes.fromhex('4000a230050040108000a2306ab3040c00000000'))
        self.assertEqual(self.elf.at(0x12d2e4,16),bytes.fromhex('70a0848f05008010000000002a53050c'))

    def test_unvoiced_profile_rejects_other_sources_speaker_changes_and_added_voice(self):
        source=decode(self.raw[CANONICAL][195])
        for changed in (source.replace('{C:81931800}','{C:81931900}'),
                        source.replace('{x00}','changed{x00}'),
                        source.replace('{C:81931800}','{C:81931800}{C:81958296590200000000}')):
            if '81958296' in changed:
                with self.assertRaises(ValueError):validate_row(source,changed)
            else:
                with self.assertRaises(ValueError):validate_row(changed,changed)
        unregistered='\n{C:81931800}New bark\n\n{x00}'
        with self.assertRaises(ValueError):validate_row(unregistered,unregistered)

    def test_exact616_unvoiced_source_and_english_match_native_parser_without_voice(self):
        original=self.raw[CANONICAL][616]
        self.assertEqual(sha(original),UNVOICED_SOURCE_616)
        source=decode(original)
        english='\n{C:81935800}Those words\nget me fired up!\n\n\n{x00}'
        wrapped,layout=wrap_row(english,self.widths,profile='battle-barks')
        self.assertEqual(validate_row(source,wrapped),'unvoiced-source-616')
        self.assertEqual(len(layout),1);self.assertEqual(layout[0]['voice'],0)
        calls=0
        for raw in (original,encode(wrapped)):
            model=pages(raw)
            self.assertEqual([p['flags'] for p in model],[0,0x11,0])
            self.assertEqual(model[1]['speaker'],88)
            self.assertTrue(all(p['voice']==p['voice_parameter']==0 for p in model))
            for page in model:
                self.assertEqual(page,native_pages.MessagePageTests.native(self,raw,page['start']));calls+=1
        self.assertEqual(calls,6)
        self.assertEqual(self.elf.at(0x12c8a4,20),bytes.fromhex('4000a230050040108000a2306ab3040c00000000'))
        self.assertEqual(self.elf.at(0x12d2e4,16),bytes.fromhex('70a0848f05008010000000002a53050c'))

    def test616_does_not_admit_generic_speaker88_or_mutated_staging(self):
        source=decode(self.raw[CANONICAL][616])
        for changed in (source.replace('{x00}','changed{x00}'),
                        source.replace('{C:81935800}','{C:81931800}'),
                        '\n{C:81935800}New bark\n\n{x00}'):
            with self.subTest(source=changed),self.assertRaises(ValueError):validate_row(changed,changed)
        for changed in (source.replace('{C:81935800}','{C:81931800}'),
                        source.replace('{C:81935800}','{C:81935800}{C:81958296590200000000}'),
                        source.replace('{C:81935800}','{C:81935800}{C:8195828601000000}'),
                        source.replace('{x00}','\n{x00}')):
            with self.subTest(english=changed),self.assertRaises(ValueError):validate_row(source,changed)

    def test_exact720_unvoiced_source_and_english_match_native_parser_without_voice(self):
        original=self.raw[CANONICAL][720]
        self.assertEqual(sha(original),UNVOICED_SOURCE_720)
        source=decode(original)
        english='\n{C:81937C00}Whoa!\n\n\n{x00}'
        wrapped,layout=wrap_row(english,self.widths,profile='battle-barks')
        self.assertEqual(validate_row(source,wrapped),'unvoiced-source-720')
        self.assertEqual(len(layout),1);self.assertEqual(layout[0]['voice'],0)
        calls=0
        for raw in (original,encode(wrapped)):
            model=pages(raw)
            self.assertEqual([p['flags'] for p in model],[0,0x11,0])
            self.assertEqual(model[1]['speaker'],124)
            self.assertTrue(all(p['voice']==p['voice_parameter']==0 for p in model))
            for page in model:
                self.assertEqual(page,native_pages.MessagePageTests.native(self,raw,page['start']));calls+=1
        self.assertEqual(calls,6)
        self.assertEqual(self.elf.at(0x12c8a4,20),bytes.fromhex('4000a230050040108000a2306ab3040c00000000'))
        self.assertEqual(self.elf.at(0x12d2e4,16),bytes.fromhex('70a0848f05008010000000002a53050c'))

    def test720_does_not_admit_generic_speaker124_or_mutated_staging(self):
        source=decode(self.raw[CANONICAL][720])
        for changed in (source.replace('{x00}','changed{x00}'),
                        source.replace('{C:81937C00}','{C:81931800}'),
                        '\n{C:81937C00}New bark\n\n{x00}'):
            with self.subTest(source=changed),self.assertRaises(ValueError):validate_row(changed,changed)
        for changed in (source.replace('{C:81937C00}','{C:81931800}'),
                        source.replace('{C:81937C00}','{C:81937C00}{C:81958296590200000000}'),
                        source.replace('{C:81937C00}','{C:81937C00}{C:8195828601000000}'),
                        source.replace('{x00}','\n{x00}')):
            with self.subTest(english=changed),self.assertRaises(ValueError):validate_row(source,changed)


    def test_exact1439_two_call_source_and_english_match_native_parser_without_voice(self):
        original=self.raw[CANONICAL][1439]
        self.assertEqual(original,self.raw[ALIAS][1439])
        self.assertEqual(sha(original),UNVOICED_SOURCE_1439)
        source=decode(original)
        english='\n{C:81931801}Come on, then!\n\n{x00}'
        wrapped,layout=wrap_row(english,self.widths,profile='battle-barks')
        self.assertEqual(validate_row(source,wrapped),'unvoiced-source-1439')
        self.assertEqual(len(layout),1);self.assertEqual(layout[0]['voice'],0)
        self.assertEqual([p['native_call'] for p in layout],[1])
        self.assertLessEqual(layout[0]['prompt_right_px'],504)
        calls=0
        for raw in (original,encode(wrapped)):
            model=pages(raw)
            self.assertEqual([p['flags'] for p in model],[0,0x11])
            self.assertEqual(model[1]['speaker'],280)
            self.assertTrue(all(p['voice']==p['voice_parameter']==p['function']==0 and not p['arguments'] for p in model))
            for page in model:
                self.assertEqual(page,native_pages.MessagePageTests.native(self,raw,page['start']));calls+=1
        self.assertEqual(calls,4)
        self.assertEqual(self.elf.at(0x12c8a4,20),bytes.fromhex('4000a230050040108000a2306ab3040c00000000'))
        self.assertEqual(self.elf.at(0x12d2e4,16),bytes.fromhex('70a0848f05008010000000002a53050c'))

    def test1439_does_not_admit_generic_speaker280_or_changed_source_staging(self):
        source=decode(self.raw[CANONICAL][1439])
        for changed in (source.replace('{x00}','changed{x00}'),
                        source.replace('{C:81931801}','{C:81931701}'),
                        source.replace('{x00}','\n{x00}'),
                        '\n{C:81931801}New bark\n\n{x00}'):
            with self.subTest(source=changed),self.assertRaises(ValueError):validate_row(changed,changed)
        for changed in (source.replace('{C:81931801}','{C:81931701}'),
                        source.replace('{C:81931801}','{C:81931801}{C:81958296590200000000}'),
                        source.replace('{C:81931801}','{C:81931801}{C:8195828601000000}'),
                        source.replace('{x00}','\n{x00}')):
            with self.subTest(english=changed),self.assertRaises(ValueError):validate_row(source,changed)
        # Even a future mistaken hash edit cannot admit the wrong speaker or
        # silently substitute the older three-call framing for this source.
        for changed in (source.replace('{C:81931801}','{C:81931701}'),
                        source.replace('{x00}','\n{x00}')):
            with patch('battle_bank.UNVOICED_SOURCE_1439',sha(encode(changed))):
                with self.subTest(profile_guard=changed),self.assertRaises(ValueError):validate_row(changed,changed)



class ResourceOriginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.elf=Elf(PATH.read_bytes())

    def fixture(self):
        ee=bytearray(0x250000);pack=bytearray(256);table=build_table([b'Word\0'])
        struct.pack_into('<I',pack,0,2);struct.pack_into('<4I',pack,4,10512,128,len(table),0);struct.pack_into('<4I',pack,20,0,256,0,0);pack[128:128+len(table)]=table
        base,node,descriptor=0x50000,0x240000,0x240100
        for va,n in LOOKUP:ee[va:va+n]=self.elf.at(va,n)
        ee[base:base+len(pack)]=pack;struct.pack_into('<I',ee,HEAD+4,node)
        struct.pack_into('<4I',ee,node,HEAD,END,base+4,descriptor);struct.pack_into('<I',ee,descriptor+12,base)
        return ee,bytes(pack),base,node,descriptor

    def test_exact_registered_member_and_packet_header_prove_physical_destination(self):
        ee,pack,base,node,descriptor=self.fixture();before=bytes(ee)
        result=origin(ee,self.elf,pack,CANONICAL,base+128)
        self.assertEqual(result['table'],CANONICAL);self.assertEqual(result['pack'],22);self.assertEqual(result['registry_nodes_checked'],1)
        self.assertIsNone(origin(ee,self.elf,pack,CANONICAL,base+132));self.assertEqual(bytes(ee),before)

    def test_bad_code_pointer_header_member_and_registry_cycle_are_rejected(self):
        for problem in ('code','pointer','header','body','cycle','duplicate'):
            ee,pack,base,node,descriptor=self.fixture()
            if problem=='code':ee[LOOKUP[0][0]]^=1
            elif problem=='pointer':struct.pack_into('<I',ee,node+8,len(ee)+1)
            elif problem=='header':ee[base+32]^=1
            elif problem=='body':ee[base+128]^=1
            elif problem=='cycle':struct.pack_into('<I',ee,node+4,node)
            else:
                struct.pack_into('<I',ee,node+4,node+16);struct.pack_into('<4I',ee,node+16,node,END,base+4,descriptor)
            with self.subTest(problem=problem),self.assertRaises(ValueError):origin(ee,self.elf,pack,CANONICAL,base+128)


if __name__=='__main__':unittest.main()
