"""Native squad UI pointers, branch paths, complete warnings and retention."""
import json,re,struct,unittest
from elf import ROOT,PATH,Elf
from test_binary import Cpu
from layout import width
from string_refs import code_refs
import formation_patch as b

class FormationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=(ROOT/'work/output/v0.2.14/SLPS_250.70').read_bytes();cls.before=Elf(cls.base);cls.source=Elf(PATH.read_bytes());cls.data,cls.report=b.patch(cls.base);cls.e=Elf(cls.data);cls.d=b.language()

    def test_every96_complete_english_object_and26_native_table_pointers(self):
        self.assertEqual(len(self.d['rows']),96)
        for r in self.d['rows']:
            a=int(self.report['addresses'][hex(r['va'])],16);raw=r['en'].encode('cp932')+b'\0'
            self.assertEqual(self.e.at(a,len(raw)),raw);self.assertIsNone(re.search('[ぁ-ゖァ-ヺ一-鿿]',r['en']))
            self.assertEqual(self.e.at(r['va'],r['source_size']),self.source.at(r['va'],r['source_size']))
        for r in self.d['pointers']:self.assertEqual(int.from_bytes(self.e.at(r['site'],4),'little'),int(self.report['addresses'][hex(r['target'])],16))

    def test_cfg_excludes_false_delay_pair_and_retains_all_saved_register_paths(self):
        src=self.source;s=next(s for s in src.sections if s['name']=='.text');entries=[x['va']for x in src.symbols if x['type']==2 and x['section']];indirect={int(k):v for k,v in self.d['indirect'].items()}
        refs=code_refs(src.at(s['va'],s['size']),s['va'],{r['va']for r in self.d['rows']if r['va']<0x238000},entries,indirect)
        a,z=0x161838,0x1686b0
        refs+=code_refs(src.at(a,z-a),a,{0x238c70,0x238c78,0x238c90},entries,indirect)
        self.assertEqual(sorted(refs,key=lambda r:(r['site'],r['lui'])),self.d['code']);self.assertEqual(len(refs),95)
        self.assertNotIn(0x109c18,{r['site']for r in refs});self.assertIn(0x163390,{r['site']for r in refs});self.assertIn(0x164340,{r['site']for r in refs})
        self.assertEqual(self.e.at(0x109bc4,0x6c),src.at(0x109bc4,0x6c))
        c=Cpu();c.put(0x109bc4,self.e.at(0x109bc4,0x6c));c.reg('v1',0);seen=[]
        c.run(0x109bc4,stop=0x109c1c,calls={0x19ee88:lambda cpu:seen.append(cpu.reg('a0'))})
        self.assertEqual(seen,[0x220890])

    def test_every_emitted_native_address_pair(self):
        for r in self.d['code']:
            if r['site'] in b.COPY_CASES:continue
            c=Cpu();c.put(0x4000,self.e.at(r['lui'],4)+self.e.at(r['site'],4)+struct.pack('<2I',0x03e00008,0));c.reg('ra',0xffff0000);c.run(0x4000)
            self.assertEqual(c.r[r['register']],int(self.report['addresses'][hex(r['target'])],16))
        r=self.d['battle_repair'][0];c=Cpu();c.put(0x4000,self.e.at(r['lui'],4)+self.e.at(r['site'],4)+struct.pack('<2I',0x03e00008,0));c.reg('ra',0xffff0000);c.run(0x4000);self.assertEqual(c.r[r['register']],r['wanted'])

    def test_actual_top_command_saved_fp_produces_both_complete_headings(self):
        create=Cpu();create.put(0x1618d8,self.e.at(0x1618d8,0xb4));create.reg('sp',0x400000);windows=[]
        create.run(0x1618d8,stop=0x16198c,calls={0x143b60:lambda cpu:None,0x1112f8:lambda cpu:windows.append((cpu.reg('t0'),cpu.reg('t2')))})
        self.assertEqual(windows[:2],[(16,160),(190,438)])
        self.assertLessEqual(windows[0][0]+windows[0][1]+8,windows[1][0])
        self.assertEqual(sum(windows[1]),628)
        c=Cpu();c.put(0x163328,self.e.at(0x163328,0x98));c.reg('sp',0x400000);c.reg('ra',0xffff0000);seen=[]
        c.run(0x163328,stop=0x1633c0,calls={0x162978:lambda cpu:None,0x1523a0:lambda cpu:None,0x1523b8:lambda cpu:seen.append(cpu.reg('a1'))})
        self.assertEqual(seen,[int(self.report['addresses']['0x2307c8'],16),int(self.report['addresses']['0x2307d8'],16)])

    def test_three_original_warning_consumers_receive_full_text_directly(self):
        for site,start in b.COPY_CASES.items():
            r=next(r for r in self.d['code']if r['site']==site);a=int(self.report['addresses'][hex(r['target'])],16);en=next(x['en']for x in self.d['rows']if x['va']==r['target'])
            c=Cpu();c.put(start,self.e.at(start,16));c.put(0x161ca4,self.e.at(0x161ca4,0x1c));c.reg('sp',0x400000);c.reg('s0',0x500000);c.reg('s3',4);c.put(0x500004,(0x600000).to_bytes(4,'little'));seen=[]
            c.run(start,stop=0x161cc0,calls={0x110ea0:lambda cpu:seen.append((cpu.reg('a0'),cpu.reg('a1')))})
            self.assertEqual(seen,[(0x600000,a)]);self.assertEqual(self.e.at(a,len(en.encode('cp932'))+1),en.encode('cp932')+b'\0')

    def test_format_arguments_controls_and_measured_compact_stats(self):
        specs=lambda s:re.findall(r'%(?:%|[-+ #0]*\d*(?:\.\d+)?[sdiufxc])',s)
        for r in self.d['rows']:
            jp=self.source.at(r['va'],r['source_size'])[:-1].decode('cp932')
            self.assertEqual(specs(jp),specs(r['en']),r['id']);self.assertEqual(re.findall(r'%%[0-9]',jp),re.findall(r'%%[0-9]',r['en']));self.assertEqual(re.findall(r'\^\d+,\d+,',jp),re.findall(r'\^\d+,\d+,',r['en']))
        widths=bytes(json.loads((ROOT/'work/output/v0.2.14/build_info.json').read_text('utf8'))['font_widths'])
        for r in self.d['layout']:
            self.assertEqual(r['widths'],[width(x,widths)for x in r['expanded_lines']]);self.assertLessEqual(max(r['widths'],default=0),504)
        for r in self.d['header_layout']:
            self.assertLessEqual(r['width'],r['limit'])
            self.assertEqual(r['width'],width(next(x['en']for x in self.d['rows']if x['id']==r['id']),widths))
        self.assertEqual(int.from_bytes(self.e.at(0x161908,4),'little'),0x240a00a0)
        empty=next(r for r in self.d['rows']if r['va']==0x238c78)
        self.assertLessEqual(len(empty['en'].encode('cp932'))+1,16)
        fmt=next(x['en']for x in self.d['rows']if x['va']==0x2311a8);self.assertIn('vs Ship(',fmt);self.assertIn('vs Unit(',fmt)

    def test_proven_pool_gap_and_every_unrelated_loaded_byte_retained(self):
        self.assertLessEqual(b.encyclopedia.END,b.BASE);self.assertLessEqual(b.BASE+self.report['payload_size'],b.LIMIT);self.assertLessEqual(b.LIMIT,b.tutorial_preview.BASE)
        changed={int(k,16)for k in self.report['patched_words']}
        for s in self.before.segments:
            if s[0]!=1:continue
            va,size=s[2],s[4];old=self.before.at(va,size);new=bytearray(self.e.at(va,size))
            for p in changed:
                if va<=p<va+size:new[p-va:p-va+4]=old[p-va:p-va+4]
            if va<=b.BASE<va+size:new[b.BASE-va:b.BASE-va+self.report['payload_size']]=bytes(self.report['payload_size'])
            self.assertEqual(bytes(new),old)
        with self.assertRaises(ValueError):b.patch(self.data)
        with self.assertRaises(ValueError):b.patch(PATH.read_bytes())

if __name__=='__main__':unittest.main()
