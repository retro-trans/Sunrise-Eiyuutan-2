"""Native warning composition, stock help geometry and long-detail transitions."""
import json,struct,unittest
from elf import ROOT,Elf
import card_dialog_patch as b
from test_binary import Cpu

class CardDialogTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=(ROOT/'work/output/v0.2.23/SLPS_250.70').read_bytes();cls.data,cls.report=b.patch(cls.before);cls.e=Elf(cls.data)
 def cpu(self):
  c=Cpu();c.reg('sp',0x500000);c.reg('ra',0xffff0000);return c
 def text(self,c,va):
  out=bytearray()
  while c.get(va,1)!=b'\0':out+=c.get(va,1);va+=1
  return out.decode('cp932')
 def test_original_initial_box_and_backing_capacity(self):
  c=self.cpu();c.put(0x1686c8,self.e.at(0x1686c8,88));c.put(0x9a61d0,self.e.at(0x9a61d0,0x230));context=0x600000;draw=[];frame=[]
  def clear(m):m.put(m.reg('a0'),bytes(m.reg('a2')))
  def create_text(m):draw.append([m.reg(r)for r in('a1','a2','a3','t0','t1')]);m.put(m.reg('a0'),struct.pack('<I',0x610000));m.put(0x610000,struct.pack('<I',0x620000))
  def create_frame(m):frame.append([m.reg(r)for r in('t0','t1')]);m.reg('v0',0x630000)
  c.run(0x1686c8,calls={0x1696b0:lambda m:m.reg('v0',context),0x19ecbc:clear,0x10c8f8:lambda m:m.reg('v0',0x640000),0x12d8c0:lambda m:None,0x12d8d0:create_text,0x110fd8:lambda m:None,0x10ed68:create_frame,0x111040:lambda m:None,0x1110f8:lambda m:None},max_steps=700)
  self.assertEqual(draw,[[118,342,504,140,0]]);self.assertEqual(frame,[[604,96]]);self.assertEqual(int.from_bytes(c.get(context+0x34,4),'little'),336)
 def test_short_long_short_transitions_restore_frame_text_and_portrait_context(self):
  c=self.cpu();c.put(b.BASE,b.code());c.put(0x12e120,self.e.at(0x12e120,8));ctx=0x600000;window=0x620000;frame=0x630000;pointer=0x640000
  c.put(ctx+4,struct.pack('<I',0x610000));c.put(0x610000,struct.pack('<I',window));c.put(ctx+0x18,struct.pack('<I',frame));c.reg('a0',ctx);c.reg('a1',pointer);c.reg('v0',0xabc);c.reg('v1',0xdef)
  for lines,y,h,th in ((3,336,96,84),(5,280,152,140),(1,336,96,84),(4,280,152,140),(3,336,96,84)):
   text='\n'.join('complete line'+str(i)for i in range(lines));c.put(pointer,text.encode()+b'\0');c.run(b.BASE,max_steps=1500)
   get=lambda at:int.from_bytes(c.get(at,4),'little')
   self.assertEqual((get(ctx+0x30),get(frame+0x1c),get(frame+0x24),get(window+0x1c),get(window+0x24)),(y,y,h,y+6,th));self.assertEqual(get(ctx+0x28),pointer);self.assertEqual(self.text(c,pointer),text);self.assertEqual((c.reg('v0'),c.reg('v1'),c.reg('a0'),c.reg('a1'),c.reg('sp')),(0xabc,0xdef,ctx,pointer,0x500000))
 def test_native_warning_no_save_and_corrupt_both_slots(self):
  for slot in(0,1):
   for mode,last in((1,'There is no save data.'),(2,'The save data is corrupted.')):
    c=self.cpu();c.put(0x152100,self.e.at(0x152100,0x264));c.put(0x224f10,self.e.at(0x224f10,20));c.put(b.TEXT,self.e.at(b.TEXT,self.report['payload_size']));c.reg('gp',0x280000);c.put(0x280000-0x776c,struct.pack('<I',mode));c.put(0x280000-0x77d0+slot*4,struct.pack('<I',0x650000));c.put(0x650000,('MEMORY CARD slot '+str(slot+1)).encode()+b'\0');draw=[];windows=[]
    def create(m):windows.append((m.reg('a0'),m.reg('a1')));m.reg('v0',0x660000)
    c.reg('a0',slot);c.reg('a1',3);c.run(0x152100,calls={0x152558:create,0x1523b8:lambda m:draw.append((self.text(m,m.reg('a1')),m.reg('a2'),m.reg('a3'))),0x142f30:lambda m:None,0x10ef50:lambda m:None},max_steps=700)
    self.assertEqual(draw,[(f'MEMORY CARD slot {slot+1}',4,0),('Sunrise Eiyuutan 2',40,1),(last,68,1)]);self.assertEqual(windows,[(380 if mode==1 else 390,102)]);self.assertEqual(c.reg('sp'),0x500000)
 def test_only_guarded_status_references_and_unused_pool_change(self):
  out=bytearray(self.data);oldelf=Elf(self.before)
  for va in self.report['patched_words']:
   off=self.e.offset(int(va,16));out[off:off+4]=self.before[off:off+4]
  for va,size in((b.BASE,self.report['code_size']),(b.TEXT,self.report['payload_size'])):
   off=self.e.offset(va);out[off:off+size]=self.before[off:off+size]
  self.assertEqual(bytes(out),self.before)
  for fn,size in((0x12dc70,60),(0x12da40,120),(0x12e120,8)):
   self.assertEqual(self.e.at(fn,size),oldelf.at(fn,size))
  for at in b.DRAWS:self.assertEqual(self.e.at(at+4,4),oldelf.at(at+4,4))
 def test_complete_warning_text_measures_inside_original_windows(self):
  widths=json.loads((ROOT/'work/output/v0.2.23/build_info.json').read_text('utf8'))['font_widths']
  for row in b.language()['rows']:
   size=sum(widths[ord(c)]+2 for c in row['en']);self.assertLessEqual(size,372 if row['va']!=0x224ed0 else 382)

if __name__=='__main__':unittest.main()
