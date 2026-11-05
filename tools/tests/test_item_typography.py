"""Native item getters, reward formatting/pagination, and typography-only delta."""
import json,struct,unittest
from test_binary import Cpu
from elf import ROOT,Elf
import item_typography_patch as b
class ItemTypographyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=(ROOT/'work/output/v0.2.27/SLPS_250.70').read_bytes();cls.data,cls.report=b.patch(cls.old);cls.e=Elf(cls.data);cls.before=Elf(cls.old);cls.d=b.language();cls.widths=json.loads((ROOT/'work/output/v0.2.27/build_info.json').read_text('utf8'))['font_widths']
 def cpu(self):
  c=Cpu();c.reg('sp',0x500000);c.reg('ra',0xffff0000)
  for lo,hi in((0x155ca8,0x155f88),(0x156038,0x1560b0),(0x1615c0,0x161818),(0x156648,0x156d00),(0x22e880,0x22e950)):
   c.put(lo,self.e.at(lo,hi-lo))
  for t in self.d['tables']:c.put(t['va'],self.e.at(t['va'],t['size']))
  for r in self.d['rows']:
   ptr=int(self.report['addresses'][hex(r['pointer'])],16);c.put(ptr,r['en'].encode('cp932')+b'\0')
  return c
 def text(self,c,p):
  out=bytearray()
  while c.get(p,1)!=b'\0':out+=c.get(p,1);p+=1
  return out.decode('cp932')
 def test_all_1005_real_full_display_omit_getters(self):
  c=self.cpu();fields={f['site']:(r,f)for r in self.d['rows']for f in r['refs']};count=0
  for table in self.d['tables']:
   for i in range(table['count']):
    for offset,suffix in((0,'Full'),(4,'Disp'),(8,'Omit')):
     site=table['va']+i*table['stride']+offset;r,f=fields[site];fn=self.e.symbol(table['prefix']+'Get'+suffix+'Name')['va'];c.reg('a0',i);c.reg('ra',0xffff0000);c.run(fn,max_steps=100)
     self.assertEqual(self.text(c,c.reg('v0')),r['en']);self.assertEqual(c.reg('sp'),0x500000);count+=1
  self.assertEqual(count,1005)
 def test_reported_native_dispatch_and_exact_reward_color_quantity_and_pages(self):
  c=self.cpu();c.reg('a0',0x712);c.run(0x156858,max_steps=500);self.assertEqual(self.text(c,c.reg('v0')),'HM Parts LvB')
  c.put(0x170170,self.e.at(0x170170,392));info=json.loads((ROOT/'work/output/v0.2.27/build_info.json').read_text('utf8'));effects=info['battle_effects'];base=int(effects['payload_va'],16);c.put(base,self.e.at(base,effects['payload_size']));c.put(0x232398,self.e.at(0x232398,16));drawn=[];grants=[];waits=[];windows=[];c.reg('ra',0xffff0000)
  def items(m):
   for i in range(9):m.put(m.reg('a0')+4*i,struct.pack('<HH',0x712,i+1))
   m.reg('v0',9)
  def create(m):windows.append(tuple(m.reg(r)for r in('a1','a2','a3','t0')));m.reg('v0',0x700000)
  def sprintf(m):m.put(m.reg('a0'),(self.text(m,m.reg('a1'))%(self.text(m,m.reg('a2')),m.reg('a3'))).encode('cp932')+b'\0')
  def draw(m):drawn.append((self.text(m,m.reg('a1')),m.reg('a3'),m.reg('t0')))
  c.run(0x170170,calls={0x1702f8:items,0x1586b0:create,0x1523b8:lambda m:None,0x19f1c0:sprintf,0x110e98:draw,0x142f30:lambda m:waits.append(m.reg('a0')),0x10ef50:lambda m:None,0x13a4c0:lambda m:grants.append((m.reg('a0'),m.reg('a1')))},max_steps=6000)
  self.assertEqual(windows,[(64,100,512,274)]);self.assertEqual(len(drawn),9);self.assertTrue(all('HM Parts LvB'in s and color==0 for s,y,color in drawn));self.assertEqual([y for s,y,color in drawn],[42+i*28 for i in range(8)]+[42]);self.assertEqual(waits,[4,4]);self.assertEqual(grants,[(0x712,i+1)for i in range(9)])
 def test_exact_character_mapping_and_every_label_width_does_not_increase(self):
  metric=lambda text:sum((self.widths[ord(c)]if ord(c)<128 else 26)+2 for c in text)
  for r in self.d['rows']:
   self.assertEqual(r['en'],r['before'].translate(b.MAP));self.assertEqual(len(r['en']),len(r['before']));self.assertLessEqual(metric(r['en']),metric(r['before']));self.assertEqual([c for c in r['en']if ord(c)>127],[c for c in r['before']if ord(c)>127 and not 0xff01<=ord(c)<=0xff5e])
  self.assertEqual(sum(r['before']!=r['en']for r in self.d['rows']),126)
 def test_only_378_name_pointers_and_new_string_pools_change(self):
  restored=bytearray(self.data)
  for va in self.report['patched_words']:
   off=self.before.offset(int(va,16));restored[off:off+4]=self.old[off:off+4]
  for p in self.report['payloads']:
   off=self.before.offset(p['va']);restored[off:off+p['size']]=self.old[off:off+p['size']]
  self.assertEqual(bytes(restored),self.old);self.assertEqual(len(self.data),len(self.old));self.assertEqual(len(self.report['patched_words']),378)
  for r in self.d['rows']:self.assertEqual(self.e.at(r['pointer'],r['size']),self.before.at(r['pointer'],r['size']))
if __name__=='__main__':unittest.main()
