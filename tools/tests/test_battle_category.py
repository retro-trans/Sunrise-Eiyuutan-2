"""Complete battle-bank inclusion, macron rendering and native SP selection."""
import json,struct,unittest
from elf import ROOT,Elf
from extract import pack_members
from textcodec import encode,decode,parse_table
from message_pages import pages
from test_binary import Cpu
import battle_category_patch as b

class BattleCategoryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  p=ROOT/'work/output/v0.2.24';cls.old=(p/'SLPS_250.70').read_bytes();cls.oldpacks={int(f.stem):f.read_bytes()for f in p.glob('*.pack')};cls.data,cls.packs,cls.r=b.patch(cls.old,cls.oldpacks);cls.e=Elf(cls.data);cls.d=b.language()
 def cpu(self):
  c=Cpu();c.reg('sp',0x500000);c.reg('ra',0xffff0000);return c
 def test_all_reviewed_rows_and_exact_held_sources_in_both_identical_tables(self):
  got=[];source=b.battle_bank.original_tables();sig=lambda p:{k:v for k,v in p.items()if k not in('start','end','body')}
  for name in b.battle_bank.TABLES:
   pn,mid=map(int,name.split('_'));pack=self.packs[pn];m=next(m for m in pack_members(pack)if m['id']==mid);rows=parse_table(pack[m['offset']:m['offset']+m['size']]);self.assertEqual(len(rows),6519);got.append(rows)
   for r in self.d['rows']:
    row=rows[r['id']];self.assertEqual(list(map(sig,pages(row))),list(map(sig,pages(source[name][r['id']]))));self.assertEqual([p['body'].split()for p in pages(row)],[p['body'].split()for p in pages(encode(r['en']))])
   for r in self.d['unresolved']:self.assertEqual(rows[r['id']],source[name][r['id']])
  self.assertEqual(got[0],got[1]);self.assertEqual(len(self.d['rows']),6463)
 def test_every_body_fits_original_three_line_box_and_native_buffer(self):
  for r in self.r['native_layout']:
   for p in r['native_layout']:
    self.assertLessEqual(len(p['lines']),3);self.assertLessEqual(max(p['widths']),504);self.assertLessEqual(p['prompt_right_px'],504);self.assertLess(p['body_bytes'],400)
 def test_supplementary_codec_actual_native_mapping_width_and_only_one_font_cell(self):
  self.assertEqual(decode(encode('Bakuryū Cutter!')),'Bakuryū Cutter!');self.assertEqual(encode('ū'),b'\x7f')
  c=self.cpu();c.put(0x108b98,self.e.at(0x108b98,40));c.reg('a0',127);c.run(0x108b98);self.assertEqual(c.reg('v0'),8460)
  c=self.cpu();c.put(b.vwf.SCALE,self.e.at(b.vwf.SCALE,100));c.put(b.vwf.TABLE,self.e.at(b.vwf.TABLE,128));c.reg('a0',127);c.reg('a1',26);c.run(b.vwf.SCALE,max_steps=100);self.assertEqual(c.reg('v0'),12)
  def font(pack):
   m=next(m for m in pack_members(pack)if m['id']==77);return pack[m['offset']:m['offset']+m['size']]
  before=font(self.oldpacks[23]);after=bytearray(font(self.packs[23]));off=self.r['glyph']['font_offset'];self.assertEqual(after[off:off+338],b.glyph()[0]);after[off:off+338]=before[off:off+338];self.assertEqual(bytes(after),before)
 def test_source_corpora_have_no_conflicting_reserved_byte_or_replaced_glyph(self):
  legacy=b'\xee\x40'.decode('cp932')
  for p in (ROOT/'work/source/text').glob('*.json'):
   d=json.loads(p.read_text('utf8'))
   for r in d.get('rows',[]):self.assertNotIn('\x7f',r.get('jp',''));self.assertNotIn(legacy,r.get('jp',''))
  for p in (ROOT/'work/source/candidates').rglob('*.json'):
   d=json.loads(p.read_text('utf8'))
   if isinstance(d,dict):
    for r in d.get('rows',[]):self.assertNotIn('\x7f',r.get('jp',''));self.assertNotIn(legacy,r.get('jp',''))
 def test_actual_native_SP_parent_child_and_original_limits_callbacks(self):
  c=self.cpu();c.put(0x16e950,self.e.at(0x16e950,0x23c));c.put(b.TEXT,self.e.at(b.TEXT,self.r['ui']['payload_size']));ship=0x600000;dev=0x610000;unit=0x620000;parent=0x630000;child=0x640000;manager=0x650000;c.put(ship+8,struct.pack('<h',30));c.put(dev+8,struct.pack('<I',0x660000));c.put(0x660000,b'Air-to-Ground Missile Cannon\0');c.put(dev+0x2c,struct.pack('<4H',2,1,5,10));c.put(child+0x14,struct.pack('<I',manager));c.put(manager+0x194,struct.pack('<I',0x670000));seen=[];draw=[];numeric=[]
  def create(m):seen.append(tuple(m.reg(r)for r in('a1','a2','a3','t0')));m.reg('v0',parent if len(seen)==1 else child)
  def text(m):
   at=m.reg('a1');raw=bytearray()
   while c.get(at,1)!=b'\0':raw+=c.get(at,1);at+=1
   draw.append(raw.decode('cp932'))
  calls={0x15c098:lambda m:m.reg('v0',34),0x155ca8:lambda m:m.reg('v0',dev),0x16eb90:lambda m:m.reg('v0',m.reg('a1')*3),0x1586b0:create,0x1523b8:text,0x114158:lambda m:numeric.append(tuple(m.reg(r)for r in('t1','t2','t3'))),0x145830:lambda m:None,0x143c08:lambda m:m.reg('v0',1),0x145808:lambda m:None,0x1141c0:lambda m:None,0x10ef50:lambda m:None}
  c.reg('a0',ship);c.reg('a1',unit);c.run(0x16e950,calls=calls,max_steps=1500);self.assertEqual(seen,[(96,100,448,128),(294,180,52,32)]);self.assertEqual(draw,['Air-to-Ground Missile Cannon','Please set SP.']);self.assertEqual(numeric,[(1,4,2)]);self.assertEqual(c.reg('v0'),2);self.assertEqual(c.reg('sp'),0x500000)
 def test_only_guarded_words_width_and_input_pool_change_in_ELF(self):
  restored=bytearray(self.data);e=Elf(self.old)
  for va in self.r['patched_words']:
   off=e.offset(int(va,16));restored[off:off+4]=self.old[off:off+4]
  off=e.offset(b.vwf.TABLE+127);restored[off]=self.old[off];off=e.offset(b.TEXT);restored[off:off+self.r['ui']['payload_size']]=self.old[off:off+self.r['ui']['payload_size']];self.assertEqual(bytes(restored),self.old)
  for pn,pack in self.oldpacks.items():
   if pn not in(22,23,4971):self.assertEqual(pack,self.packs[pn])

if __name__=='__main__':unittest.main()
