"""Execute native saved-name getter and exact default display mapping."""
import unittest,json,struct
from elf import ROOT,Elf
from test_binary import Cpu
from layout import width
import squad_name_patch as b
class SquadNameTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=(ROOT/'work/output/v0.2.17/SLPS_250.70').read_bytes();cls.before=Elf(cls.base);cls.data,cls.report=b.patch(cls.base);cls.e=Elf(cls.data);cls.en=b.language()['rows'][0]['en'].encode();cls.source=cls.before.at(b.SOURCE,15)
 def cpu(self):
  c=Cpu();c.put(0x1679C8,self.e.at(0x1679C8,92));c.put(b.BASE,b.code());c.put(b.SOURCE,self.source);c.put(b.TEXT,self.en+b'\0');c.reg('a0',0x600000);c.reg('ra',0xffff0000);c.reg('sp',0x500000);c.reg('s0',1234);return c
 def test_default_in_existing_save_maps_only_temporary_buffer(self):
  c=self.cpu();raw=bytes([0x55])*8+self.source+b'Z'+bytes([0xaa])*40;c.put(0x600000,raw);c.run(0x1679C8,max_steps=1500);self.assertEqual(c.reg('v0'),0x63aee8);self.assertEqual(c.get(c.reg('v0'),15),self.en+b'\0');self.assertEqual(c.get(0x600000,len(raw)),raw);self.assertEqual(c.reg('sp'),0x500000);self.assertEqual(c.reg('s0'),1234)
 def test_all_single_byte_near_matches_and_custom_names_remain(self):
  cases=[b'',b'Alpha',b'Retake Norstan',b'ABCDEFGHIJKLMNOP',self.source[:-1]+b'X']
  for i in range(14):
   raw=bytearray(self.source);raw[i]^=1;cases.append(bytes(raw))
  for raw in cases:
   c=self.cpu();record=raw.ljust(17,b'\0');c.put(0x600008,record);c.run(0x1679C8,max_steps=1500);wanted=record[:16].split(b'\0')[0]+b'\0';self.assertEqual(c.get(c.reg('v0'),len(wanted)),wanted,raw);self.assertEqual(c.get(0x600008,len(record)),record)
 def test_actual_new_game_argument_and_native_copy_capacity(self):
  c=self.cpu();c.put(0x10259C,self.e.at(0x10259C,20));c.reg('s0',7);seen=[]
  c.run(0x10259C,stop=0x1025B0,calls={0x1620A0:lambda m:seen.append((m.reg('a0'),m.reg('a1'),m.reg('a2')))});self.assertEqual(seen,[(204,7,b.TEXT)]);self.assertEqual(c.get(b.TEXT,15),self.en+b'\0');self.assertEqual(self.e.at(0x162100,4),struct.pack('<I',0x24060010))
  widths=bytes(json.loads((ROOT/'work/output/v0.2.17/build_info.json').read_text('utf8'))['font_widths']);self.assertEqual(width(self.en.decode(),widths),178);self.assertLessEqual(width(self.en.decode(),widths),334)
 def test_exact_prior_bytes_and_all_four_consumers_retained(self):
  reconstructed=bytearray(self.data)
  for site in self.report['patched_words']:
   va=int(site,16);off=self.before.offset(va);reconstructed[off:off+4]=self.base[off:off+4]
  for va,size in [(b.BASE,len(b.code())),(b.TEXT,len(self.en)+1)]:reconstructed[self.before.offset(va):self.before.offset(va)+size]=bytes(size)
  self.assertEqual(bytes(reconstructed),self.base)
  for site in (0x163654,0x16386C,0x163AF0,0x167B30):self.assertEqual(self.e.at(site,4),self.before.at(site,4))
  with self.assertRaises(ValueError):b.patch(self.data)
if __name__=='__main__':unittest.main()
