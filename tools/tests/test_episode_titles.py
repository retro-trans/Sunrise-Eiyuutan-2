"""Execute native concatenation and font-fit code for every independent index pair."""
import unittest,struct,json
from test_binary import Cpu
from elf import ROOT,Elf
import episode_titles_patch as b
class EpisodeTitleTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=(ROOT/'work/output/v0.2.26/SLPS_250.70').read_bytes();cls.data,cls.report=b.patch(cls.old);cls.e=Elf(cls.data);cls.lang=json.loads(b.LANGUAGE.read_text('utf8'));cls.widths=json.loads((ROOT/'work/output/v0.2.26/build_info.json').read_text('utf8'))['font_widths']
 def cpu(self):
  c=Cpu();c.reg('sp',0x700000);c.reg('ra',0xffff0000)
  for va,size in((0x13e6a8,600),(0x221de8,76),(0x221f68,76),(b.BASE,b.END-b.BASE)):c.put(va,self.e.at(va,size))
  for p in self.lang['prefixes']:c.put(p['pointer'],bytes.fromhex(p['raw_hex'])+b'\0')
  return c
 def raw(self,c,p):
  data=bytearray()
  while c.get(p,1)!=b'\0':data+=c.get(p,1);p+=1
  return bytes(data)
 def test_all_361_native_getter_pairs_complete_text_and_buffer_canaries(self):
  def strlen(c):c.reg('v0',len(self.raw(c,c.reg('a0'))))
  def memcpy(c):c.put(c.reg('a0'),c.get(c.reg('a1'),c.reg('a2')));c.reg('v0',c.reg('a0'))
  for case in self.report['combinations']:
   c=self.cpu();c.put(b.BUFFER-1,b'Q');c.put(b.END,b'Z');c.put(0x51d6c0,b'OLD'*14);c.reg('a0',case['prefix']);c.reg('a1',case['title']);c.reg('s4',0xdeadbeef)
   c.run(0x13e6a8,calls={0x19f7d8:strlen,0x19ec0c:memcpy},max_steps=400)
   self.assertEqual(c.reg('v0'),b.BUFFER);self.assertEqual(self.raw(c,b.BUFFER),case['text'].encode('cp932'));self.assertEqual(c.get(b.BUFFER-1,1),b'Q');self.assertEqual(c.get(b.END,1),b'Z');self.assertEqual(c.get(0x51d6c0,42),b'OLD'*14);self.assertEqual(c.reg('s4'),0xdeadbeef)
 def test_all_native_fits_and_actual_save_list_render_argument_instructions(self):
  for case in self.report['combinations']:
   c=self.cpu();text=case['text'];c.put(0x600000,text.encode('cp932')+b'\0');c.reg('a0',0x600000);c.reg('a1',26);c.reg('s0',77);c.reg('s1',88)
   def measure(m):self.assertEqual(self.raw(m,m.reg('a0')).decode('cp932'),text);m.reg('v0',b.width(text,m.reg('a1'),self.widths))
   c.run(b.BASE,calls={0x10e510:measure},max_steps=400);self.assertEqual(c.reg('t8'),case['font']);self.assertEqual(c.reg('v0'),case['width']);self.assertLessEqual(c.reg('v0'),462);self.assertEqual((c.reg('s0'),c.reg('s1')),(77,88))
   c.put(0x150004,self.e.at(0x150004,8));c.run(0x150004,stop=0x15000c);self.assertEqual((c.reg('a2'),c.reg('a3')),(case['font'],case['font']))
   if case['font']<26:self.assertGreater(b.width(text,case['font']+1,self.widths),462)
 def test_only_19_title_pointers_nine_instructions_and_reserved_pool_change(self):
  restored=bytearray(self.data);old=Elf(self.old)
  for va in self.report['patched_words']:
   off=old.offset(int(va,16));restored[off:off+4]=self.old[off:off+4]
  off=old.offset(b.BASE);restored[off:off+self.report['payload_size']]=self.old[off:off+self.report['payload_size']]
  self.assertEqual(bytes(restored),self.old);self.assertEqual(len(self.data),len(self.old));self.assertEqual(len(self.report['patched_words']),28)
  self.assertEqual(self.e.at(0x221de8,76),old.at(0x221de8,76));self.assertEqual(self.e.at(b.BUFFER,64),bytes(64))
 def test_unaligned_doubleword_copy_interpreter_all_offsets(self):
  from mips import i_type,pack
  for offset in range(8):
   c=Cpu();c.put(0x1000,bytes(range(32)));c.reg('a0',0x1000+offset);c.reg('a1',0x2000+offset);c.reg('v0',0xdeadbeefdeadbeef)
   c.put(0x3000,pack([i_type(0x1a,'a0','v0',7),i_type(0x1b,'a0','v0',0),i_type(0x2c,'a1','v0',7),i_type(0x2d,'a1','v0',0)]));c.run(0x3000,stop=0x3010)
   self.assertEqual(c.get(0x2000+offset,8),bytes(range(offset,offset+8)))
if __name__=='__main__':unittest.main()
