"""Native class/captain getters and proportional formation rendering safeguards."""
import json,struct,unittest,re
from test_binary import Cpu
from elf import ROOT,Elf
import formation_readability_patch as b
class FormationReadabilityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=(ROOT/'work/output/v0.2.28/SLPS_250.70').read_bytes();cls.data,cls.report=b.patch(cls.old);cls.e=Elf(cls.data);cls.before=Elf(cls.old);cls.d=b.language();cls.widths=json.loads((ROOT/'work/output/v0.2.28/build_info.json').read_text('utf8'))['font_widths']
 def text(self,c,p):
  out=bytearray()
  while c.get(p,1)!=b'\0':out+=c.get(p,1);p+=1
  return out.decode('cp932')
 def cpu(self):
  c=Cpu();c.reg('sp',0x700000);c.reg('ra',0xffff0000);c.put(b.BASE,self.e.at(b.BASE,b.CODE_END-b.BASE))
  for r in self.report['fields']:c.put(r['pointer'],r['en'].encode('cp932')+b'\0')
  return c
 def metric(self,text,size):return sum((self.widths[ord(ch)]*size//26 if ord(ch)<128 else size)+2 for ch in text)
 def test_all_99_class_and_364_captain_getters_and_actual_submenu_pointers(self):
  c=self.cpu()
  for a,n in((0x155bb8,0x78),(0x156e28,0xb0),(0x1552b0,0x88),(0x155330,0x48),(0x1e3100,528),(0x1e8820,8052),(0x1d5810,860*64)):c.put(a,self.e.at(a,n))
  fields={f['site']:f for f in self.report['fields']}
  for i in range(33):
   for k,fn in((0,0x155bd0),(4,0x155bf0),(8,0x155c10)):
    c.reg('a0',i);c.reg('ra',0xffff0000);c.run(fn);f=fields[0x1e3100+i*16+k];self.assertEqual(self.text(c,c.reg('v0')),f['en'])
  for i in range(183):
   pilot=int.from_bytes(self.e.at(0x1e8820+i*44,2),'little')
   if pilot==1:continue
   for off,fn in((0,0x156e60),(4,0x156e88)):
    c.reg('a0',i);c.reg('ra',0xffff0000);c.run(fn,max_steps=200);f=fields[0x1d5810+pilot*64+off];self.assertEqual(self.text(c,c.reg('v0')),f['en'])
  for site,text in((0x238c80,'Ship'),(0x238c84,' Captain ')):
   ptr=int.from_bytes(self.e.at(site,4),'little');self.assertEqual(self.text(c,ptr),text)
 def test_all_machine_and_device_omission_labels_fit_square_fonts_and_keep_row_arguments(self):
  labels=['[Add Machine]','[Add Equipment]']
  for name,stride in(('mch_info',64),('it_devi_info',60),('it_mchdev_info',64)):
   table=self.e.symbol(name)
   for i in range(table['size']//stride):
    ptr=int.from_bytes(self.e.at(table['va']+i*stride+8,4),'little');caption=self.e.at(ptr,512).split(b'\0')[0].decode('cp932');labels.append('['+caption+']'if name=='it_mchdev_info'else caption+'  Sz 99')
  c=self.cpu();c.put(0x600020,struct.pack('<I',272));seen=[]
  for text in labels:
   c.put(0x610000,text.encode('cp932')+b'\0');args=dict(a0=0x600000,a1=0x610000,a2=14,a3=26,t0=4,t1=5,t2=84,t3=7)
   for reg,val in args.items():c.reg(reg,val)
   def measure(m):m.reg('v0',self.metric(self.text(m,m.reg('a0')),m.reg('a1')))
   def draw(m):seen.append({r:m.reg(r)for r in args});m.reg('v0',0x620000)
   c.reg('ra',0xffff0000);c.run(b.LIST,calls={0x10e510:measure,0x112868:draw},max_steps=800);result=seen[-1];size=result['a2'];self.assertEqual(result,dict(args,a2=size,a3=size));self.assertLessEqual(self.metric(text,size),264,text);self.assertEqual(c.reg('v0'),0x620000);self.assertEqual(c.reg('sp'),0x700000)
   if size<26:self.assertGreater(self.metric(text,size+1),264)
  self.assertGreater(len(seen),750)
 def test_right_class_size_and_expanded_stat_lines_fit_without_truncation(self):
  cases=[]
  for f in self.report['fields']:
   if f['category']=='class'and f.get('field')=='full':
    cases.append((b.CLASS,f['en'],0,228,True));cases.append((b.CLASS,f['en']+'\u3000'*11,0,228,True));cases.append((b.CLASS,f['en']+' '*8,0,228,True))
  for value in(0,2,99,255):cases.append((b.SIZE,'Sz '+str(value),244,64,True))
  for air in('Flying','Anti-Air','Ground'):
   for reach in('Short','Long'):
    for value in(0,30,999,9999):cases.append((b.ROW,f'HPMax {value} [{air}・{reach}]',0,308,False))
  cases.extend((b.ROW,s,x,308-x,False)for s,x in(('ENMax 999 Launch EN999',0),('S10 L 6 P10',46),('LM Cannon Null',46),('Attack AT999 EN999',0),('Defend DF999 EN999',0),('Special AT999 EN999',0)))
  c=self.cpu()
  for entry,text,x,limit,explicit in cases:
   c.put(0x610000,text.encode('cp932')+b'\0');args=dict(a0=0x600000,a1=0x610000,a2=x,a3=28,t0=14 if explicit else 3,t1=28,t2=4);seen=[]
   for reg,v in args.items():c.reg(reg,v)
   def measure(m):m.reg('v0',self.metric(self.text(m,m.reg('a0')),m.reg('a1')))
   def draw(m):seen.append({r:m.reg(r)for r in args})
   c.reg('ra',0xffff0000);c.run(entry,calls={0x10e510:measure,0x110ea0:draw},max_steps=1600);result=seen[0];size=result['t0'];visible=text.rstrip(' \u3000')if entry==b.CLASS else text;self.assertEqual(result,dict(args,t0=size,t1=size,t2=4 if explicit else 3));self.assertLessEqual(self.metric(visible,size),limit,text);self.assertEqual(c.reg('sp'),0x700000);self.assertEqual(self.text(c,0x610000),text)
   if entry==b.CLASS and self.metric(visible,26)<=limit:self.assertEqual(size,26)
 def test_actual_saved_fp_machine_and_device_list_formatters(self):
  for fn,getname,getsize in((0x166360,0x154ee8,0x154f68),(0x167308,0x155d00,0x155d88)):
   c=self.cpu();c.put(fn,self.e.at(fn,0x118));c.put(self.report['format_va'],b'%s  Sz %1d\0');c.put(0x610000,b'Air-to-Ground Missile Cannon\0');c.put(0x600020,struct.pack('<I',272));c.put(0x600900,struct.pack('<2H',1,2));c.reg('a0',0x5f0000);c.reg('a1',0x600000);c.reg('a2',0x600900);seen=[]
   def sprintf(m):
    fmt=self.text(m,m.reg('a1'));self.assertEqual(fmt,'%s  Sz %1d');m.put(m.reg('a0'),(fmt%(self.text(m,m.reg('a2')),m.reg('a3'))).encode('cp932')+b'\0')
   def measure(m):m.reg('v0',self.metric(self.text(m,m.reg('a0')),m.reg('a1')))
   def row(m):seen.append((self.text(m,m.reg('a1')),m.reg('a2'),m.reg('a3'),m.reg('t2'),m.reg('t3')));m.reg('v0',0x620000)
   c.run(fn,calls={0x111bb0:lambda m:None,getname:lambda m:m.reg('v0',0x610000),getsize:lambda m:m.reg('v0',2),0x19f1c0:sprintf,0x10e510:measure,0x112868:row},max_steps=16000)
   self.assertEqual(len(seen),2);self.assertEqual([s[3:]for s in seen],[(0,1),(28,2)]);self.assertTrue(all(s[0]=='Air-to-Ground Missile Cannon  Sz 2'and s[1]==s[2]for s in seen));self.assertEqual(c.reg('sp'),0x700000)
 def test_exact_permitted_delta_and_protected_player_and_normal_help_geometry(self):
  restored=bytearray(self.data)
  for va in self.report['patched_words']:
   off=self.before.offset(int(va,16));restored[off:off+4]=self.old[off:off+4]
  for p in self.report['payloads']+[dict(va=b.BASE,size=self.report['code_size'])]:
   off=self.before.offset(p['va']);restored[off:off+p['size']]=self.old[off:off+p['size']]
  self.assertEqual(bytes(restored),self.old)
  for p in self.d['protected_player']:self.assertEqual(self.e.at(p['site'],4),self.before.at(p['site'],4))
  self.assertEqual(self.e.at(0x1d5810+64,64),self.before.at(0x1d5810+64,64));self.assertEqual(self.e.at(0x1686c8,88),self.before.at(0x1686c8,88));self.assertEqual(self.e.at(0x9b78c0,0xa0),self.before.at(0x9b78c0,0xa0))
if __name__=='__main__':unittest.main()
