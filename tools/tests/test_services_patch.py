"""Native services consumers, typed records, complete text and retained bytes."""
import json,re,struct,unittest
from elf import ROOT,PATH,Elf
from test_binary import Cpu
from string_refs import code_refs
import services_patch as b

class ServicesTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=(ROOT/'work/output/v0.2.15/SLPS_250.70').read_bytes();cls.before=Elf(cls.base);cls.source=Elf(PATH.read_bytes());cls.data,cls.report=b.patch(cls.base);cls.e=Elf(cls.data);cls.d=b.language();cls.widths=bytes(json.loads((ROOT/'work/output/v0.2.15/build_info.json').read_text('utf8'))['font_widths'])
 def address(self,va):return int(self.report['addresses'][hex(va)],16)
 def test_complete193_objects_and35_static_consumers(self):
  self.assertEqual(len(self.d['rows']),193);self.assertEqual(len(self.d['pointers']),35)
  for r in self.d['rows']:
   raw=r['en'].encode('cp932')+b'\0';self.assertEqual(self.e.at(self.address(r['va']),len(raw)),raw)
   self.assertIsNone(re.search('[ぁ-ゖァ-ヺ一-鿿]',r['en']));self.assertNotIn('jp',r)
   self.assertEqual(self.e.at(r['va'],r['source_size']),self.source.at(r['va'],r['source_size']))
  for r in self.d['pointers']:self.assertEqual(int.from_bytes(self.e.at(r['site'],4),'little'),self.address(r['target']))
 def test_cfg_scope_and22_executed_address_pairs(self):
  s=next(s for s in self.source.sections if s['name']=='.text');entries=[x['va']for x in self.source.symbols if x['type']==2 and x['section']]
  targets={r['va'] for r in self.d['rows'][:51]}
  refs=code_refs(self.source.at(s['va'],s['size']),s['va'],targets,entries)
  refs=[r for r in refs if r['target']<0x237800 or 0x13F360<=r['site']<0x13FDA8 or 0x1696E8<=r['site']<0x16A218]
  self.assertEqual(sorted(refs,key=lambda r:(r['site'],r['lui'])),self.d['code']);self.assertEqual(len(refs),22)
  for r in refs:
   c=Cpu();c.put(0x4000,self.e.at(r['lui'],4)+self.e.at(r['site'],4)+struct.pack('<2I',0x03e00008,0));c.reg('ra',0xffff0000);c.run(0x4000)
   self.assertEqual(c.r[r['register']],self.address(r['target']))
 def test_all71_part_records_and_four_actual_getters(self):
  self.assertEqual(len(self.d['parts']['fields']),284)
  for r in self.d['parts']['records']:
   va=r['va'];self.assertEqual(self.e.at(va+16,16),self.source.at(va+16,16))
   for off,func in zip((0,4,8,12),(0x1615D8,0x1615F8,0x161618,0x161638)):
    c=Cpu();c.put(0x1615C0,self.e.at(0x1615C0,0x98));c.put(0x1F7C30,self.e.at(0x1F7C30,2272));c.reg('sp',0x400000);c.reg('ra',0xffff0000);c.reg('a0',r['index']);c.run(func)
    self.assertEqual(c.reg('v0'),self.address(r['pointers'][off//4]))
 def test_actual_shared_attribute_getters_and_null_entries(self):
  for fun,table,labels in ((0x168678,0x1F8890,['Ground','Anti-Air','Flying']),(0x168690,0x1F88A0,['Short','Long','Pierce'])):
   for i in range(4):
    c=Cpu();c.put(0x168678,self.e.at(0x168678,0x30));c.put(table,self.e.at(table,16));c.reg('a0',i);c.reg('ra',0xffff0000);c.run(fun)
    if i==3:self.assertEqual(c.reg('v0'),0)
    else:self.assertEqual(self.e.at(c.reg('v0'),len(labels[i])+1),labels[i].encode()+b'\0')
 def test20_docking_labels_reach_original_native_list_print(self):
  self.assertEqual(self.e.at(0x1FD498,16),self.source.at(0x1FD498,16))
  for i in range(1,21):
   table=0x1FD498;self.assertEqual(self.e.at(table+i*16+4,12),self.source.at(table+i*16+4,12))
   c=Cpu();c.put(0x16C968,self.e.at(0x16C968,0x58));c.put(table,self.e.at(table,336));c.put(0x400000,bytes([i]));c.reg('sp',0x400000)
   for reg,v in [('s2',0),('s3',0),('s4',1),('s5',0x500000),('s6',table),('s7',512)]:c.reg(reg,v)
   seen=[]
   def font(cpu):seen.append(('font',cpu.reg('a0'),cpu.reg('a1')))
   def render(cpu):seen.append(('render',cpu.reg('a1'),cpu.reg('a2'),cpu.reg('a3')));cpu.reg('v0',0x600000)
   c.run(0x16C968,stop=0x16C9C0,calls={0x10E510:font,0x112868:render})
   ptr=int.from_bytes(self.e.at(table+i*16,4),'little')
   self.assertEqual(seen,[('font',ptr,13),('render',ptr,26,26)]);self.assertEqual(int.from_bytes(c.get(0x60001c,4),'little'),512)
 def test_hp_font_tail_preserves_caller_and_complete_attributes(self):
  c=Cpu();c.put(b.STATS_FONT,self.e.at(b.STATS_FONT,16));values={'a0':0x400000,'a1':0x500000,'a2':0,'a3':28,'ra':0x16A120}
  for k,v in values.items():c.reg(k,v)
  c.run(b.STATS_FONT,stop=0x110EA0)
  for k,v in values.items():self.assertEqual(c.reg(k),v)
  self.assertEqual([c.reg(x)for x in('t0','t1','t2')],[22,26,0])
  self.assertEqual(int.from_bytes(self.e.at(0x16A118,4),'little'),0x0C000000|(b.STATS_FONT>>2));self.assertEqual(self.e.at(0x16A11c,4),self.source.at(0x16A11c,4))
  hp=next(r for r in self.d['layout']if r['id']==next(x['id']for x in self.d['rows']if x['va']==0x231310))
  self.assertEqual((hp['font_width'],hp['max_width'],len(hp['expanded_lines'])),(22,292,9));self.assertLessEqual(max(hp['widths']),292)
 def test_controls_word_preserving_reflow_and_all_layout_profiles(self):
  specs=lambda s:re.findall(r'%(?:%|[-+ #0]*\d*(?:\.\d+)?[sdiufxc])',s)
  for r in self.d['rows']:
   jp=self.source.at(r['va'],r['source_size'])[:-1].decode('cp932');self.assertEqual(specs(jp),specs(r['en']),r['id']);self.assertEqual(re.findall(r'\^\d+,\d+,',jp),re.findall(r'\^\d+,\d+,',r['en']))
  for r in self.d['layout']:
   size=r['font_width'];metric=lambda s:sum((self.widths[ord(c)]*size//26 if ord(c)<128 else size)+2 for c in s)
   self.assertEqual(r['widths'],[metric(x) for x in r['expanded_lines']]);self.assertLessEqual(max(r['widths'],default=0),r['max_width'],r['id'])
  self.assertEqual(len(self.d['reflow']),18)
  for r in self.d['reflow']:self.assertEqual(r['before'].split(),r['after'].split());self.assertLessEqual(len(r['after'].splitlines()),2)
  for va in (0x221790,0x222110):self.assertEqual(next(r['en']for r in self.d['rows']if r['va']==va).count('\u3000'),12)
  self.assertEqual(next(r['en']for r in self.d['rows']if r['va']==0x22F988),'S-Gorongo Parts')
 def test_reserved_gap_and_all_unrelated_loaded_bytes_retained(self):
  self.assertLessEqual(b.BASE+self.report['payload_size'],b.LIMIT);self.assertLess(b.STATS_FONT+16,0x9A8000)
  changed={int(k,16) for k in self.report['patched_words']}
  for s in self.before.segments:
   if s[0]!=1:continue
   va,size=s[2],s[4];old=self.before.at(va,size);new=bytearray(self.e.at(va,size))
   for p in changed:
    if va<=p<va+size:new[p-va:p-va+4]=old[p-va:p-va+4]
   for start,n in((b.BASE,self.report['payload_size']),(b.STATS_FONT,16)):
    if va<=start<va+size:new[start-va:start-va+n]=bytes(n)
   self.assertEqual(bytes(new),old)
  with self.assertRaises(ValueError):b.patch(self.data)
  with self.assertRaises(ValueError):b.patch(PATH.read_bytes())

if __name__=='__main__':unittest.main()
