"""Native ability getters, scoped status constructors, and reward pagination."""
import json,re,struct,unittest
from elf import ROOT,Elf
from test_binary import Cpu
import battle_effects_patch as b

class BattleEffectsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=(ROOT/'work/output/v0.2.21/SLPS_250.70').read_bytes();cls.data,cls.report=b.patch(cls.old);cls.e=Elf(cls.data);cls.before=Elf(cls.old);cls.d=b.language()
 def cpu(self):
  c=Cpu();c.reg('sp',0x500000);c.reg('ra',0xffff0000);return c
 def text(self,c,va):
  out=bytearray()
  while c.get(va,1)!=b'\0':out+=c.get(va,1);va+=1
  return out.decode('cp932')
 def test_all63_strings_and122_fields_with_two_unchanged_sentinels(self):
  addresses={int(r['source_va'],16):int(r['va'],16)for r in self.report['layout']};self.assertEqual(len(addresses),63)
  for row in self.d['rows']:
   self.assertEqual(self.e.at(row['va'],row['source_size']),self.before.at(row['va'],row['source_size']))
   for s in row['sites']:
    p=int.from_bytes(self.e.at(int(s['pointer_site'],16),4),'little')
    self.assertEqual(p,addresses.get(row['va'],row['va']))
   if row['translation_required']:
    item=next(s for s in self.report['layout']if int(s['source_va'],16)==row['va']);raw=item['display'].encode('cp932')+b'\0'
    self.assertEqual(self.e.at(addresses[row['va']],len(raw)),raw);self.assertEqual(row['en'].split(),item['display'].split())
    self.assertFalse(re.search('[ぁ-ゖァ-ヺ一-鿿]',item['display']))
  self.assertEqual(self.e.at(0x22ad70,16),self.before.at(0x22ad70,16));self.assertEqual(self.e.at(0x232380,8),self.before.at(0x232380,8))
 def test_actual_four_native_getters_for_all31_records(self):
  c=self.cpu();c.put(0x155b20,self.e.at(0x155b20,152));c.put(0x1e2f10,self.e.at(0x1e2f10,31*16))
  for record in range(31):
   for field,fn in enumerate((0x155b38,0x155b58,0x155b78,0x155b98)):
    c.reg('a0',record);c.reg('ra',0xffff0000);c.run(fn)
    self.assertEqual(c.reg('v0'),int.from_bytes(self.e.at(0x1e2f10+record*16+field*4,4),'little'));self.assertEqual(c.reg('sp'),0x500000)
 def test_actual_scoped_status_constructor_and_original_callbacks(self):
  c=self.cpu();c.put(0x1686c8,self.e.at(0x1686c8,88));c.put(b.INIT,self.e.at(b.INIT,b.CODE_END-b.INIT));context=0x600000;draw=[];frame=[];threads=[]
  def clear(m):m.put(m.reg('a0'),bytes(m.reg('a2')))
  def create_text(m):
   draw.append([m.reg(r)for r in('a1','a2','a3','t0','t1')]);m.put(m.reg('a0'),struct.pack('<I',0x610000));m.put(0x610000,struct.pack('<I',0x620000))
  def create_frame(m):frame.append([m.reg(r)for r in('a0','a1','a2','a3','t0','t1')]);m.reg('v0',0x630000)
  def thread(m):threads.append([m.reg(r)for r in('a0','a1','a2','a3')]);m.reg('v0',0x640000)
  c.run(0x1686c8,calls={0x1696b0:lambda m:m.reg('v0',context),0x19ecbc:clear,0x10c8f8:thread,0x12d8c0:lambda m:None,
   0x12d8d0:create_text,0x110fd8:lambda m:None,0x10ed68:create_frame,0x111040:lambda m:None,0x1110f8:lambda m:None},max_steps=700)
  self.assertEqual(draw,[[118,286,504,140,0]]);self.assertEqual(frame,[[1,2,513,2,604,152]])
  self.assertEqual(threads,[[0x12dcb0,0x41000,0x41000,0x2000]])
  self.assertEqual(int.from_bytes(c.get(context+4+0x30,4),'little'),280)
  self.assertEqual(int.from_bytes(c.get(0x630000+0x1c,4),'little'),280);self.assertEqual(c.reg('v0'),context);self.assertEqual(c.reg('sp'),0x500000)
 def test_all_comments_keep_words_fit_five_rows_and_native256_byte_buffer(self):
  comments=[r for r in self.report['layout']if r['comment']];self.assertEqual(len(comments),30)
  for r in comments:self.assertLessEqual(len(r['widths']),3);self.assertLessEqual(max(r['widths']),504);self.assertEqual(r['en'].split(),r['display'].split())
  phase=next(r for r in comments if r['source_va']=='0x22af90');self.assertIn('attack phase, damage taken is 75',phase['en']);self.assertEqual(len(phase['widths']),2)
  for file in ('battle-details.en.json','formation.en.json'):
   for r in json.loads((ROOT/'work/translation/en'/file).read_text('utf8'))['rows']:
    if r['va']not in (0x222868,0x22edc0,0x22ee00,0x2305e8,0x230650,0x231030):continue
    specs=[s for s in re.findall(r'%(?:%|[-+ #0]*\d*(?:\.\d+)?[sdiufxc])',r['en'])if s!='%%']
    for comment in comments:
     vals=[comment['display']if i==len(specs)-1 else('Anti-Air'if s.endswith('s')else 999)for i,s in enumerate(specs)]
     rendered=r['en']%tuple(vals);self.assertLess(len(rendered.encode('cp932')),256);self.assertLessEqual(len(rendered.splitlines()),5)
 def load_item_paths(self,c):
  for at,n in((0x156858,0x110),(0x156af8,0x180),(0x1616e0,0x80),(0x22e880,40),(0x22e910,40),(0x1f8510,672),(0x9a6b00,0xd00),(0x9b7400,0xc00)):
   c.put(at,self.e.at(at,n))
 def test_actual_reward_getter_returns_english_HM_parts_without_changing_item_id(self):
  c=self.cpu();self.load_item_paths(c);c.reg('a0',0x712);c.run(0x156858,max_steps=500)
  self.assertEqual(self.text(c,c.reg('v0')),'ＨＭ Parts ＬｖＢ');self.assertEqual(c.reg('sp'),0x500000)
 def test_actual_reward_window_nine_items_two_pages_and_original_grants(self):
  c=self.cpu();self.load_item_paths(c);c.put(0x170170,self.e.at(0x170170,392));c.put(b.TEXT,self.e.at(b.TEXT,self.report['payload_size']));c.put(0x232398,self.e.at(0x232398,16));windows=[];headings=[];drawn=[];grants=[];waits=[]
  def items(m):
   for i in range(9):m.put(m.reg('a0')+4*i,struct.pack('<HH',0x712,i+1))
   m.reg('v0',9)
  def create(m):windows.append([m.reg(r)for r in('a1','a2','a3','t0')]);m.reg('v0',0x700000)
  def sprintf(m):m.put(m.reg('a0'),(self.text(m,m.reg('a1'))%(self.text(m,m.reg('a2')),m.reg('a3'))).encode('cp932')+b'\0')
  c.run(0x170170,calls={0x1702f8:items,0x1586b0:create,0x1523b8:lambda m:headings.append(self.text(m,m.reg('a1'))),
   0x19f1c0:sprintf,0x110e98:lambda m:drawn.append((self.text(m,m.reg('a1')),m.reg('a3'))),0x142f30:lambda m:waits.append(m.reg('a0')),
   0x10ef50:lambda m:None,0x13a4c0:lambda m:grants.append((m.reg('a0'),m.reg('a1')))},max_steps=6000)
  self.assertEqual(headings,['Acquired Items']);self.assertEqual(windows,[[64,100,512,274]])
  self.assertEqual(len(drawn),9);self.assertEqual([y for s,y in drawn],[42+i*28 for i in range(8)]+[42]);self.assertTrue(all('ＨＭ Parts ＬｖＢ'in s for s,y in drawn))
  self.assertEqual(waits,[4,4]);self.assertEqual(grants,[(0x712,i+1)for i in range(9)]);self.assertEqual(c.reg('sp'),0x500000)
 def test_only_guarded_words_and_proven_zero_intervals_change(self):
  masked=bytearray(self.data)
  for va in self.report['patched_words']:
   off=self.e.offset(int(va,16));masked[off:off+4]=self.old[off:off+4]
  for va,n in((b.TEXT,self.report['payload_size']),(b.INIT,self.report['code_size'])):
   off=self.e.offset(va);masked[off:off+n]=self.old[off:off+n]
  self.assertEqual(bytes(masked),self.old)
  for va,n,copy in b.CLONES:self.assertEqual(self.e.at(va,n),self.before.at(va,n))
  self.assertEqual(len(self.report['patched_words']),127)
  with self.assertRaises(ValueError):b.patch(self.data)

if __name__=='__main__':unittest.main()
