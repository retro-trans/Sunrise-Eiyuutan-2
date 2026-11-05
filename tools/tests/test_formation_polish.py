"""Execute native formation consumers; guard IDs, fits, buffers and exact delta."""
import unittest,json,struct,re
from test_binary import Cpu
from elf import ROOT,Elf
import formation_polish_patch as b
class FormationPolishTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=(ROOT/'work/output/v0.2.29/SLPS_250.70').read_bytes();cls.data,cls.report=b.patch(cls.old);cls.e=Elf(cls.data);cls.before=Elf(cls.old);cls.widths=json.loads((ROOT/'work/output/v0.2.29/build_info.json').read_text('utf8'))['font_widths']
 def string(self,p):return self.e.at(p,256).split(b'\0')[0].decode('cp932')
 def text(self,c,p):
  raw=bytearray()
  while c.get(p,1)!=b'\0':raw+=c.get(p,1);p+=1
  return raw.decode('cp932')
 def metric(self,t,s):return sum((self.widths[ord(c)]*s//26 if ord(c)<128 else s)+2 for c in t)
 def cpu(self):
  c=Cpu();c.reg('sp',0x700000);c.reg('ra',0xffff0000);c.reg('gp',0x5f0000)
  for a,n in((b.BASE,b.END-b.BASE),(0x9a4000,128),(0x9a4100,0x50),(0x162e78,8),(0x1669a0,260)):c.put(a,self.e.at(a,n))
  return c
 def test_all_submenus_and_eight_unmanned_machine_records(self):
  for site,text in b.MENUS.items():self.assertEqual(self.string(int.from_bytes(self.e.at(site,4),'little')),text)
  for i in range(532):
   for off in(0,4,8):
    site=0x1cd310+i*64+off;old=int.from_bytes(self.before.at(site,4),'little');new=int.from_bytes(self.e.at(site,4),'little');text=self.string(new)
    self.assertNotIn('Unmanned Unit',text)
    if i in b.UNMANNED:self.assertEqual(text,self.string(old).replace('Unmanned Unit','Unmanned'))
    else:self.assertEqual(old,new)
 def test_actual_pilot_list_keeps_ids_and_normal_square_font(self):
  c=self.cpu();c.put(0x600020,struct.pack('<I',272));c.put(0x600900,struct.pack('<3H',2,3,4));c.reg('a0',0x5e0000);c.reg('a1',0x600000);c.reg('a2',0x600900);seen=[]
  labels={2:'Domon',3:'Rie',4:'A long complete pilot caption'}
  def name(m):m.put(0x610000,labels[m.reg('a0')].encode()+b'\0');m.reg('v0',0x610000)
  def sprintf(m):self.assertEqual(self.text(m,m.reg('a1')),'%s');m.put(m.reg('a0'),m.get(m.reg('a2'),100).split(b'\0')[0]+b'\0')
  # Native pilot formatter uses the original "%s" object.
  c.put(0x238d48,b'%s\0')
  def row(m):seen.append(tuple(m.reg(r)for r in('a2','a3','t2','t3')));m.reg('v0',0x620000)
  c.run(0x1669a0,calls={0x111bb0:lambda m:None,0x155378:name,0x19f1c0:sprintf,0x112868:row},max_steps=30000)
  self.assertEqual([v[2:]for v in seen],[(0,1),(28,2),(56,3)]);self.assertEqual(seen[0][:2],(26,26));self.assertTrue(all(x==y for x,y,_,_ in seen));self.assertEqual(c.reg('sp'),0x700000)
 def test_equipment_all_names_slots_font_choice_and_safe_buffers(self):
  labels=[self.string(int.from_bytes(self.e.at(0x1e46a0+i*64+8,4),'little'))for i in range(161)];seen_sizes=set()
  for slots in range(4):
   for name in labels:
    c=self.cpu();c.put(0x5f0000-0x690c,struct.pack('<I',0x600000));c.put(0x610000,name.encode('cp932')+b'\0');c.reg('a0',0x620000);seen=[];items=[]
    def unit(m):self.assertEqual(m.reg('a0'),0x620000);m.reg('v0',1)
    def count(m):self.assertEqual(m.reg('a0'),1);m.reg('v0',slots)
    def item(m):self.assertEqual(m.reg('a0'),0x620000);items.append(m.reg('a1'));m.reg('v0',1)
    def sprintf(m):
     fmt=self.text(m,m.reg('a1'));self.assertEqual(fmt,'#2Equipment %d:%s');text=fmt%(m.reg('a2'),self.text(m,m.reg('a3')));self.assertLess(len(text.encode('cp932'))+1,128);m.put(m.reg('a0'),text.encode('cp932')+b'\0')
    def setter(m):self.assertEqual(m.reg('a0'),0x600000);seen.append(self.text(m,m.reg('a1')))
    c.run(0x162e78,calls={0x15c058:unit,0x154f88:count,0x15cbd0:item,0x156090:lambda m:m.reg('v0',0x610000),0x19f1c0:sprintf,0x1687e8:setter},max_steps=60000)
    self.assertEqual(items,list(range(1,slots+1)));self.assertEqual(len(seen),1);self.assertLess(len(seen[0].encode('cp932'))+1,256)
    if not slots:self.assertEqual(seen[0],'')
    else:
     self.assertTrue(seen[0].endswith('#2'));lines=seen[0][:-2].split('\n');self.assertEqual(len(lines),slots)
     for n,line in enumerate(lines,1):
      match=re.fullmatch(r'#([012])(Equipment \d:.*)',line);self.assertIsNotNone(match);size=(13,20,26)[int(match[1])];seen_sizes.add(size);self.assertEqual(match[2],f'Equipment {n}:{name}');self.assertLessEqual(self.metric(match[2],size),504)
      expected=next(s for s in(26,20,13)if self.metric(match[2],s)<=504);self.assertEqual(size,expected)
     self.assertLessEqual(sum((13,20,26)[int(line[1])]+2 for line in lines),84)
    self.assertEqual(c.reg('sp'),0x700000)
  self.assertEqual(seen_sizes,{13,20,26})
 def test_exact_delta_keeps_normal_help_and_dynamic_player(self):
  restored=bytearray(self.data)
  for va in self.report['patched_words']:
   off=self.before.offset(int(va,16));restored[off:off+4]=self.old[off:off+4]
  for p in self.report['payloads']:
   off=self.before.offset(p['va']);restored[off:off+p['size']]=self.old[off:off+p['size']]
  self.assertEqual(bytes(restored),self.old)
  for a,n in((0x1686c8,88),(0x9b78c0,0xa0),(0x1d5850,64),(0x238c80,4)):self.assertEqual(self.e.at(a,n),self.before.at(a,n))
if __name__=='__main__':unittest.main()
