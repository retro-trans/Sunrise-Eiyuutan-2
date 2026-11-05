"""Whole special-name table preservation and native selection geometry."""
import json,struct,unittest
from elf import ROOT,Elf,PATH
from test_binary import Cpu
import special_names_patch as b
class SpecialNameTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=(ROOT/'work/output/v0.2.25/SLPS_250.70').read_bytes();cls.data,cls.r=b.patch(cls.old);cls.e=Elf(cls.data);cls.source=Elf(PATH.read_bytes());cls.expected={(f['row'],f['field']):f for f in cls.r['fields']}
 def cpu(self):
  c=Cpu();c.reg('sp',0x500000);c.reg('ra',0xffff0000)
  for at,size in((0x1fd5e8,7080),(b.BASE,self.r['payload_size']),(0x16f068,0x60),(0x16f570,0x18)):c.put(at,self.e.at(at,size))
  return c
 def text(self,c,ptr):
  buf=bytearray()
  while c.get(ptr,1)!=b'\0':buf+=c.get(ptr,1);ptr+=1
  return buf.decode('ascii')
 def test_all_354_actual_native_getters_and_full_display_omission_distinctions(self):
  for i in range(118):
   for field,at in((4,0x16f068),(8,0x16f088),(12,0x16f0a8)):
    c=self.cpu();c.reg('a0',i);c.run(at,max_steps=100);f=self.expected[i,field];self.assertEqual(c.reg('v0'),f['pointer']);self.assertEqual(self.text(c,c.reg('v0')),f['en'])
  self.assertEqual(self.expected[45,4]['en'],'Omnidirectional Mega-Particle Cannon');self.assertEqual(self.expected[45,12]['en'],'Omni. Mega-Particle Cannon');self.assertEqual(self.expected[94,4]['en'],'Arago');self.assertEqual(self.expected[94,12]['en'],'Full Power')
 def test_each_omit_name_in_actual_native_selector_on_both_sides(self):
  widths=json.loads((ROOT/'work/output/v0.2.25/build_info.json').read_text('utf8'))['font_widths']
  for i in range(118):
   for flag,x in((0,16),(128,224)):
    c=self.cpu();c.put(0x16f208,self.e.at(0x16f208,0x14c));lst=0x600000;flags=0x610000;win=0x620000;row=0x630000;c.put(lst,struct.pack('<H',i));c.put(flags,struct.pack('<I',flag));c.put(win+0x20,struct.pack('<I',400));created=[];draw=[]
    def create(m):created.append(tuple(m.reg(r)for r in('a1','a2','a3','t0')));m.reg('v0',win)
    def measure(m):m.reg('v0',sum(widths[ord(v)]+2 for v in self.text(c,m.reg('a0'))))
    def line(m):draw.append((self.text(c,m.reg('a1')),m.reg('a2'),m.reg('a3'),m.reg('t2'),m.reg('t3')));m.reg('v0',row)
    calls={0x1586b0:create,0x111bb0:lambda m:None,0x10e510:measure,0x112868:line,0x113a78:lambda m:m.reg('v0',1),0x111c90:lambda m:None,0x158730:lambda m:None}
    c.reg('a0',lst);c.reg('a1',1);c.reg('a2',flags);c.run(0x16f208,calls=calls,max_steps=500);f=self.expected[i,12]
    self.assertEqual(created,[(x,130,400,28)]);self.assertEqual(draw,[(f['en'],26,26,0,1)]);self.assertEqual(int.from_bytes(c.get(row+0x1c,4),'little'),400);self.assertEqual(int.from_bytes(c.get(row+0x28,4),'little'),200-f['width']//2);self.assertLessEqual(f['width'],384);self.assertEqual(c.reg('v0'),1)
 def test_only_name_pointers_five_selector_words_and_new_string_pool_change(self):
  restored=bytearray(self.data);old=Elf(self.old)
  for va in self.r['patched_words']:
   off=old.offset(int(va,16));restored[off:off+4]=self.old[off:off+4]
  off=old.offset(b.BASE);restored[off:off+self.r['payload_size']]=self.old[off:off+self.r['payload_size']];self.assertEqual(bytes(restored),self.old)
  self.assertEqual(len(self.data),len(self.old));self.assertEqual(len(self.r['fields']),354)
if __name__=='__main__':unittest.main()
