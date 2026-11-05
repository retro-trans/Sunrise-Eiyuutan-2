"""Execute Trade list/requirement consumers and check every native recipe."""
import unittest,json,struct,re
from test_binary import Cpu
from elf import ROOT,Elf
import trade_patch as b

class TradeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=(ROOT/'work/output/v0.2.30/SLPS_250.70').read_bytes();cls.data,cls.report=b.patch(cls.old);cls.e=Elf(cls.data);cls.before=Elf(cls.old);cls.widths=json.loads((ROOT/'work/output/v0.2.30/build_info.json').read_text('utf8'))['font_widths']
 def text(self,c,p):
  out=bytearray()
  while c.get(p,1)!=b'\0':out+=c.get(p,1);p+=1
  return out.decode('cp932')
 def metric(self,t,s=26):return sum((self.widths[ord(ch)]*s//26 if ord(ch)<128 else s)+2 for ch in t)
 def cpu(self):
  c=Cpu();c.reg('sp',0x700000);c.reg('ra',0xffff0000)
  for a,n in((b.BASE,b.END-b.BASE),(0x13d490,0x148),(0x13d5f0,0x148),(0x1c25a0,3072)):c.put(a,self.e.at(a,n))
  c.put(0x51d368,bytes(range(128)));return c
 def name(self,kind,index):
  table,stride={4:(0x1e34d0,60),5:(0x1e46a0,64),6:(0x1e4448,40),8:(0x1f8510,32)}[kind];p=int.from_bytes(self.e.at(table+index*stride+8,4),'little');return self.e.at(p,200).split(b'\0')[0].decode('cp932')
 def hooks(self,seen,owned):
  def item(m):m.reg('v0',(m.reg('a0')<<12)|m.reg('a1'))
  def name(m):
   item_id=m.reg('a0');caption=self.name(item_id>>12,item_id&4095);m.put(0x630000,caption.encode('cp932')+b'\0');m.reg('v0',0x630000)
  def sprintf(m):
   fmt=self.text(m,m.reg('a1'));tokens=re.findall(r'%(?:-?\d+)?[sd]',fmt);args=[m.reg(r)for r in('a2','a3','t0','t1','t2','t3')];vals=[self.text(m,v)if t.endswith('s')else v for t,v in zip(tokens,args)];out=fmt%tuple(vals);seen.append((m.reg('a0'),out));m.put(m.reg('a0'),out.encode('cp932')+b'\0');m.reg('v0',len(out.encode('cp932')))
  return {0x156c78:item,0x156858:name,0x13a3b8:lambda m:m.reg('v0',owned),0x19f1c0:sprintf,0x19f7d8:lambda m:m.reg('v0',len(self.text(m,m.reg('a0')).encode('cp932')))}
 def test_actual_list_item_formatter_for_every_recipe(self):
  for i in range(128):
   for owned in(0,1,99):
    c=self.cpu();seen=[];c.reg('a0',i+1);c.run(0x13d518,calls=self.hooks(seen,owned),max_steps=1000);kind,index=struct.unpack('<2H',self.e.at(0x1c25a0+i*24+4,4));name=self.name(kind,index);text=self.text(c,c.reg('v0'));self.assertEqual(text,f'\x1e{name}\t{owned}');self.assertEqual(c.reg('v0'),b.BUFFER);self.assertLessEqual(len(text.encode('cp932'))+1,64);self.assertLessEqual(self.metric(name,26 if self.metric(name)<=520 else 22),520);self.assertEqual(c.reg('sp'),0x700000)
 def test_actual_callback_all_requirements_keep_counts_positions_and_full_names(self):
  for i in range(128):
   for owned in(0,99):
    c=self.cpu();seen=[];shown=[];calls=self.hooks(seen,owned);calls[0x12dbd8]=lambda m:shown.append(self.text(m,m.reg('a0')));c.reg('a1',0x600000);c.reg('a2',0x610000);c.reg('a3',0x620000);c.put(0x610010,struct.pack('<I',0x620000));c.put(0x620024,struct.pack('<I',i+1));c.run(0x13d5f0,calls=calls,max_steps=1500)
    self.assertEqual(len(shown),1);self.assertEqual(len(seen),3)
    for slot in range(2):
     kind,index,needed=struct.unpack('<HHI',self.e.at(0x1c25a0+i*24+8+slot*8,8));name=self.name(kind,index)if kind else'None';row=f'#2{name}#2^320,{slot*28},{needed:2d} (Owned {owned:2d})';self.assertEqual(seen[slot][1],row);self.assertLess(len(row.encode('cp932'))+1,65);self.assertLessEqual(self.metric(name),312);self.assertLessEqual(self.metric(f'{needed:2d} (Owned {owned:2d})'),184)
    full=f'^0,0,{seen[0][1]}^0,28,{seen[1][1]}^0,56,Trade the items above for this item.';self.assertEqual(shown[0],full);self.assertLess(len(full.encode('cp932'))+1,512);self.assertLessEqual(self.metric('Trade the items above for this item.'),504);self.assertEqual(c.reg('v0'),0);self.assertEqual(c.reg('sp'),0x700000)
  # Inactive and unchanged-selection callbacks retain the original early exit.
  c=self.cpu();c.reg('a1',0x600000);c.reg('a2',0x610000);c.reg('a3',0x620000);c.run(0x13d5f0,max_steps=200);self.assertEqual(c.reg('v0'),0)
 def test_all_reference_pairs_and_shared_alert_and_marker_fallback(self):
  for r in self.report['rows']:
   for h,l in r['pairs']:
    high=int.from_bytes(self.e.at(h,4),'little')&65535;low=int.from_bytes(self.e.at(l,4),'little')&65535;p=(high<<16)+(low-65536 if low&32768 else low);self.assertEqual(p,r['pointer']);self.assertEqual(self.e.at(p,256).split(b'\0')[0].decode('cp932'),r['en'])
  self.assertEqual(int.from_bytes(self.e.at(0x13d7e4,4),'little'),b.addiu('s4','zero',608));self.assertEqual(int.from_bytes(self.e.at(0x13bbe8,4),'little'),b.jal(b.DEFAULT))
  c=self.cpu();c.put(b.columns.DEFAULT_RENDER,self.e.at(b.columns.DEFAULT_RENDER,0x40));c.put(0x610000,b'Ordinary subtitle\0');c.reg('a0',0x600000);c.reg('a1',0x610000);c.reg('a2',4);c.reg('a3',8);c.reg('t0',3);seen=[];c.run(b.DEFAULT,calls={0x110e98:lambda m:seen.append(tuple(m.reg(r)for r in('a0','a1','a2','a3','t0')))},max_steps=60);self.assertEqual(seen,[(0x600000,0x610000,4,8,3)])
  c=self.cpu();c.put(0x610000,b'\x1fLegacy item\t99\0');c.reg('a0',0x600000);c.reg('a1',0x610000);c.reg('t0',26);c.reg('t1',26);seen=[];c.run(b.ROW,calls={b.columns.RENDER:lambda m:seen.append((m.reg('a0'),m.reg('a1'),m.reg('t0'),m.reg('t1')))},max_steps=40);self.assertEqual(seen,[(0x600000,0x610000,26,26)])
  for text,trade in((b'Plain item\0',False),(b'\x1fOld columns\0',False),(b'\x1eNew columns\0',True)):
   c=self.cpu();c.put(0x610000,text);c.reg('a0',0x610000);c.reg('a1',26);seen=[]
   def old_measure(m):seen.append((m.reg('a0'),m.reg('a1')));m.reg('v0',123)
   c.run(b.MEASURE,calls={b.columns.MEASURE:old_measure},max_steps=40);self.assertEqual(c.reg('v0'),608 if trade else 123);self.assertEqual(seen,[]if trade else[(0x610000,26)])
 def test_actual_trade_columns_keep_square_fonts_complete_labels_and_alignment(self):
  for label in('Item','S-EN Charger','Improved Ultra-Compact Nuclear Fusion Engine'):
   c=self.cpu();c.put(b.prior.MEASURE,self.e.at(b.prior.MEASURE,0xc0));c.put(0x9a4000,self.e.at(0x9a4000,128));c.put(0x9a4100,self.e.at(0x9a4100,0x50));text='\x1e'+label+'\t'+('Owned'if label=='Item'else'99');c.put(0x610000,text.encode()+b'\0');c.reg('a0',0x600000);c.reg('a1',0x610000);c.reg('a2',0);c.reg('a3',0);c.reg('t0',0);seen=[]
   def draw(m):seen.append((self.text(m,m.reg('a1')),m.reg('a2'),m.reg('t0'),m.reg('t1'),m.reg('t2')))
   c.run(b.DEFAULT,calls={0x110ea0:draw},max_steps=20000);size=26 if self.metric(label)<=520 else 22;self.assertEqual(seen[0],(label,8,size,size,0));self.assertEqual(seen[1][2:],(26,26,0));self.assertEqual(seen[1][1]+self.metric(seen[1][0]),600);self.assertEqual(self.text(c,0x610000),text)
 def test_exact_delta_preserves_trade_rules_recipes_and_normal_help(self):
  restored=bytearray(self.data)
  for va in self.report['patched_words']:
   off=self.before.offset(int(va,16));restored[off:off+4]=self.old[off:off+4]
  for p in self.report['payloads']:
   off=self.before.offset(p['va']);restored[off:off+p['size']]=self.old[off:off+p['size']]
  self.assertEqual(bytes(restored),self.old)
  for a,n in((0x1c25a0,3072),(0x13daf0,0x48),(0x13db5c,0x4c),(0x12da40,120),(0x9b78c0,0xa0),(0x1d5850,64)):self.assertEqual(self.e.at(a,n),self.before.at(a,n))
if __name__=='__main__':unittest.main()
