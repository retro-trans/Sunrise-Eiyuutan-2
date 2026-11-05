"""Execute compiled consumers and protect complete battle-category boundaries."""
import json,re,struct,unittest
from elf import ROOT,PATH,Elf
from layout import width
from test_binary import Cpu
import battle_details_patch as b

class BattleDetailsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=(ROOT/'work/output/v0.2.13/SLPS_250.70').read_bytes();cls.before=Elf(cls.base)
        cls.data,cls.report=b.patch(cls.base);cls.e=Elf(cls.data);cls.d=b.language()

    def test_all1986_typed_fields_reach_complete_saved_english(self):
        self.assertEqual(self.report['coverage']['unit_records'],532)
        self.assertEqual(len(self.d['rows']),838)
        for r in self.report['resolved_fields']:
            a=int(r['pointer'],16);site=int(r['site'],16);raw=r['en'].encode('cp932')+b'\0'
            self.assertEqual(int.from_bytes(self.e.at(site,4),'little'),a)
            self.assertEqual(self.e.at(a,len(raw)),raw)
            self.assertIsNone(re.search('[ぁ-ゖァ-ヺ一-鿿]',r['en']))

    def test_actual_full_display_short_name_getters_for532_records(self):
        c=Cpu();table=self.e.symbol('mch_info')['va'];c.put(table,self.e.at(table,532*64));c.put(0x154e90,self.e.at(0x154e90,0x78))
        for row in range(532):
            for field,fn in ((0,0x154ea8),(4,0x154ec8),(8,0x154ee8)):
                c.reg('a0',row);c.reg('sp',0x400000);c.reg('ra',0xffff0000);c.run(fn)
                self.assertEqual(c.reg('v0'),int.from_bytes(self.e.at(table+row*64+field,4),'little'))

    def test_all51_native_address_pairs_and24_ui_pointers(self):
        self.assertEqual((len(self.d['code']),len(self.d['pointers'])),(51,24))
        for r in self.d['code']:
            c=Cpu();c.put(0x4000,self.e.at(r['lui'],4)+self.e.at(r['site'],4)+struct.pack('<2I',0x03e00008,0));c.reg('ra',0xffff0000);c.run(0x4000)
            self.assertEqual(c.r[r['register']],int(self.report['addresses'][hex(r['target'])],16))
        for r in self.d['pointers']:self.assertEqual(int.from_bytes(self.e.at(r['site'],4),'little'),int(self.report['addresses'][hex(r['target'])],16))
        for site,text in ((0x1c5a50,'Cannon'),(0x1c5a54,'Support'),(0x1c5a58,'Support')):
            a=int.from_bytes(self.e.at(site,4),'little');self.assertEqual(self.e.at(a,len(text)+1),text.encode('ascii')+b'\0')

    def test_real_finish_function_copies27_aligned_bytes_and_returns(self):
        c=Cpu();c.put(0x148980,self.e.at(0x148980,0x74));a=int(self.report['addresses']['0x2225c8'],16)
        self.assertEqual(a%8,0);c.put(a,self.e.at(a,27));c.reg('sp',0x400000);c.reg('ra',0xffff0000)
        seen=[]
        def available(cpu):cpu.reg('v0',0)
        def confirm(cpu):seen.append(cpu.get(cpu.reg('a0'),27));cpu.reg('v0',1)
        c.run(0x148980,calls={0x143c08:available,0x145b78:confirm})
        self.assertEqual(seen,[b'Finish?\0'+bytes(19)]);self.assertEqual(c.reg('v0'),1);self.assertEqual(c.reg('sp'),0x400000)

    def test_all81_paragraphs_fit_two_lines_without_lost_words(self):
        widths=bytes(json.loads((ROOT/'work/output/v0.2.13/build_info.json').read_text('utf8'))['font_widths'])
        self.assertEqual(len(self.d['descriptions']),81)
        for r in self.d['descriptions']:
            self.assertLessEqual(len(r['lines']),2);self.assertEqual(' '.join(r['lines']).split(),r['en'].split())
            self.assertEqual(r['widths'],[width(s,widths) for s in r['lines']]);self.assertTrue(all(n<=504 for n in r['widths']))
        ds={r['row']:r['en'] for r in self.d['descriptions'] if r['table']=='it_devi_info'}
        self.assertIn('AB/OM/people only',ds[51]);self.assertIn('no AB/OM/people',ds[52])
        self.assertTrue(all('Special abilities' in ds[n] for n in range(50,54)))

    def test_printf_color_caret_contracts_and_runtime_stat_fit(self):
        specs=lambda s:re.findall(r'%(?:%|[-+ #0]*\d*(?:\.\d+)?[sdiufxc])',s)
        colors=lambda s:re.findall(r'%%[0-9]',s)
        positions=lambda s:re.findall(r'\^\d+,\d+,',s)
        original=Elf(PATH.read_bytes())
        for r in self.d['rows']:
            if 'battle-ui' not in r['groups']:continue
            jp=original.at(r['va'],r['source_size'])[:-1].decode('cp932')
            self.assertEqual(specs(jp),specs(r['en']),r['id']);self.assertEqual(colors(jp),colors(r['en']),r['id']);self.assertEqual(positions(jp),positions(r['en']),r['id'])
        widths=bytes(json.loads((ROOT/'work/output/v0.2.13/build_info.json').read_text('utf8'))['font_widths'])
        fmt=next(r['en'] for r in self.d['rows'] if r['va']==0x2227d8)
        for attr in ('Flying','Anti-Air','Ground'):
            for ran in ('Long','Short','Pierce'):
                rendered=fmt%(attr,ran,999,999,999,999,999,999,99,99,99,'LM Cannon Null')
                for x,y,s in re.findall(r'\^(\d+),(\d+),([^\^]*)',rendered):
                    self.assertLessEqual(int(x)+width(re.sub(r'%[0-9]','',s),widths),200,(x,s))

    def test_readable_selectors_fit_both_native_sides(self):
        self.assertEqual(max(r['width'] for r in self.d['short_label_layout']),383)
        for r in self.d['short_label_layout']:self.assertLessEqual(r['width'],384)
        for r in self.d['geometry']:self.assertEqual(int.from_bytes(self.e.at(r['site'],4),'little'),r['value'])
        self.assertTrue(all(0<=x and x+400<=640 for x in self.report['mirrored_selector_x']))
        for site in (0x146d58,0x146d80,0x147214,0x14723c):self.assertEqual(int.from_bytes(self.e.at(site,4),'little')&65535,26)
        for site in (0x146d84,0x147240):self.assertEqual(self.e.at(site,4),self.before.at(site,4))

    def test_only_approved_loaded_words_change_and_reject_wrong_baseline(self):
        changed={int(k,16) for k in self.report['patched_words']}
        for seg in self.before.segments:
            if seg[0]!=1:continue
            va,size=seg[2],seg[4];old=self.before.at(va,size);new=bytearray(self.e.at(va,size))
            for p in changed:
                if va<=p<va+size:new[p-va:p-va+4]=old[p-va:p-va+4]
            self.assertEqual(bytes(new),old)
        for table,count,stride,first in (('mch_info',532,64,12),('it_devi_info',66,60,20),('it_expend_info',15,40,16)):
            va=self.e.symbol(table)['va']
            for n in range(count):self.assertEqual(self.e.at(va+n*stride+first,stride-first),self.before.at(va+n*stride+first,stride-first))
        self.assertLessEqual(b.BASE+self.report['payload_size'],0x9c0000)
        with self.assertRaises(ValueError):b.patch(self.data)
        with self.assertRaises(ValueError):b.patch(PATH.read_bytes())

if __name__=='__main__':unittest.main()
