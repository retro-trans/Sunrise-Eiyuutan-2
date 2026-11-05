"""Execute interactive native consumers; check full category and retained bytes."""
import json,re,struct,unittest
from elf import ROOT,Elf
from extract import pack_members
from textcodec import parse_table,decode,encode
from message_pages import pages
from story_layout import pieces
from layout import width
from test_binary import Cpu
import battle_readability_patch as b

class BattleReadabilityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=ROOT/'work/output/v0.2.20';cls.old=(cls.base/'SLPS_250.70').read_bytes();cls.packs={int(p.stem):p.read_bytes()for p in cls.base.glob('*.pack')}
  cls.data,cls.newpacks,cls.report=b.patch(cls.old,cls.packs);cls.e=Elf(cls.data);cls.before=Elf(cls.old)
  cls.widths=bytes(json.loads((cls.base/'build_info.json').read_text('utf8'))['font_widths'])
 def readstr(self,c,p):
  out=bytearray()
  while c.get(p,1)!=b'\0':out+=c.get(p,1);p+=1
  return out.decode('cp932')
 def cpu(self):
  c=Cpu();c.reg('sp',0x400000);c.reg('ra',0xffff0000);return c
 def selector(self,name,side,low_en=False,alternate=False):
  fn,size={'launch':(0x146570,684),'item':(0x146ea0,612),'repair':(0x147c48,648)}[name]
  c=self.cpu();c.put(fn,self.e.at(fn,size));ship,records,win,sel=0x500000,0x510000,0x520000,0x530000
  c.put(ship,struct.pack('<I',side*128)+bytes(4)+struct.pack('<h',10 if low_en else 70)+bytes(34)+struct.pack('<H',100))
  c.reg('a0',ship);labels=['Impulse 7','GT-A','Air-to-Ground Missile Cannon'];strings={}
  for i,text in enumerate(labels):
   at=0x550000+i*256;c.put(at,text.encode()+b'\0');strings[i]=at
  if name=='repair':
   for i in range(48):c.put(records+i*48,struct.pack('<IIhh',0,i%3,20,60 if i<3 else 20)+bytes(36))
  elif name=='launch':
   for i in range(48):c.put(records+i*48,struct.pack('<IIhh',1 if i<3 else 0,i%3,60,60)+bytes(36))
  else:
   for i in range(48):c.put(records+i*12,struct.pack('<IIhh',0,i%3,1,0))
  calls=[];rows=[];selected=[]
  def getrecords(cpu):cpu.reg('v0',records)
  def validdev(cpu):cpu.reg('v0',int(cpu.reg('a0')<records+36))
  def getname(cpu):cpu.reg('v0',strings[cpu.reg('a0')])
  def cost(cpu):cpu.reg('v0',15)
  def measure(cpu):
   self.assertEqual(cpu.reg('a1'),26);cpu.reg('v0',width(self.readstr(cpu,cpu.reg('a0')),self.widths))
  def create(cpu):
   args=[cpu.reg(r)for r in ('a0','a1','a2','a3','t0')];calls.append(args)
   cpu.put(win+0x14,struct.pack('<I',win+0x400));cpu.put(win+0x20,struct.pack('<I',args[3]));cpu.reg('v0',win)
  def add(cpu):
   ptr=sel+len(rows)*256;rows.append(dict(pointer=ptr,text=self.readstr(cpu,cpu.reg('a1')),args=[cpu.reg(r)for r in ('a2','a3','t0','t1','t2','t3')]))
   cpu.reg('v0',ptr)
  def choose(cpu):selected.append(cpu.reg('a0'));cpu.reg('v0',0)
  def mode(cpu):cpu.reg('v0',2 if alternate else 0)
  stubs={0x1462B0:getrecords,0x1462D0:getrecords,0x16D1F8:validdev,0x1586B0:create,0x111BB0:lambda c:None,
   0x145AF0:lambda c:c.reg('v0',1),0x15C1B0:cost,0x15C0B8:getname,0x15C128:getname,0x10E510:measure,
   0x112868:add,0x143C08:mode,0x158738:choose,0x16C198:choose,0x16C300:choose,0x111C90:lambda c:None,0x158730:lambda c:None}
  c.run(fn,calls=stubs,max_steps=3000)
  self.assertEqual(calls,[[1,16 if side==0 else 224,122,400,196]])
  self.assertEqual(selected,[win]);self.assertEqual(len(rows),3)
  for i,r in enumerate(rows):
   self.assertEqual(r['text'],labels[i]);self.assertEqual(r['args'][:2],[26,26]);self.assertEqual(r['args'][3:],[0,i*28,i+1])
   self.assertEqual(int.from_bytes(c.get(r['pointer']+0x1c,4),'little'),400)
   self.assertEqual(int.from_bytes(c.get(r['pointer']+0x28,4),'little'),200-width(labels[i],self.widths)//2)
   self.assertEqual(r['args'][2],int(low_en) if name=='launch' else (int(low_en and not alternate) if name=='item' else 0))
  self.assertEqual(c.reg('sp'),0x400000);self.assertEqual(c.reg('v0'),0)
  if name!='repair':self.assertEqual(int.from_bytes(c.get(win+0x400+0x168,4),'little'),0x146500 if name=='launch' else 0x146e30)
 def test_actual_interactive_selectors_both_sides_en_and_input_modes(self):
  for name in ('launch','item','repair'):
   for side in (0,1):
    for low_en in (False,True):
     for alternate in (False,True):
      with self.subTest(name=name,side=side,low_en=low_en,alternate=alternate):self.selector(name,side,low_en,alternate)
 def test_actual_prompt_helper_centers_real_proportional_measurement(self):
  for text in ('EN to use for Cannon:','EN to use for Support:','Please enter an amount.','EN to use for repairs:','Air-to-Ground Missile Cannon','Save slot 12'):
   for font in (22,26):
    c=self.cpu();c.put(0x152478,self.e.at(0x152478,144));c.put(0x500020,struct.pack('<I',400));c.put(0x510000,text.encode()+b'\0')
    c.reg('a0',0x500000);c.reg('a1',0x510000);c.reg('a2',64);c.reg('a3',7);c.reg('t0',font)
    seen=[]
    def measured(cpu):
     self.assertEqual((cpu.reg('a0'),cpu.reg('a1')),(0x510000,font));cpu.reg('v0',sum(self.widths[ord(x)]*font//26+2 for x in text))
    def draw(cpu):seen.append([cpu.reg(r)for r in ('a0','a1','a2','a3','t0','t1','t2')])
    c.run(0x152478,calls={0x10E510:measured,0x110EA0:draw})
    pixels=sum(self.widths[ord(x)]*font//26+2 for x in text)
    self.assertEqual(seen,[[0x500000,0x510000,(400-pixels)//2,64,font,26,7]]);self.assertEqual(c.reg('sp'),0x400000)
 def test_all_longest_labels_and_amount_text_fit_at_normal_width(self):
  d=json.loads((ROOT/'work/translation/en/battle-details.en.json').read_text('utf8'))
  for row in d['short_label_layout']:self.assertLessEqual(row['width'],384)
  for text in ('EN to use for Cannon:','EN to use for Support:','Please enter an amount.','EN to use for repairs:'):self.assertLessEqual(width(text,self.widths),384)
  for site in (0x14754c,0x147568,0x14806c,0x148088,0x1480a4):self.assertEqual(int.from_bytes(self.e.at(site,4),'little')&65535,26)
  for site in (0x1475a8,0x14811c):self.assertEqual(int.from_bytes(self.e.at(site,4),'little')&65535,158)
 def test_all172_messages_preserve_words_voices_speakers_and_native_calls(self):
  raw=self.newpacks[4970];m=next(m for m in pack_members(raw)if m['id']==10511);rows=parse_table(raw[m['offset']:m['offset']+m['size']]);self.assertEqual(len(rows),172)
  source=(ROOT/'work/source/afs/RESOURCE/04970.bin').read_bytes();m=next(m for m in pack_members(source)if m['id']==10511);old=parse_table(source[m['offset']:m['offset']+m['size']])
  sig=lambda p:{k:v for k,v in p.items()if k not in('start','end','body')}
  for r in b.language()['rows']:
   i=r['id'];self.assertEqual(list(map(sig,pages(old[i]))),list(map(sig,pages(rows[i]))))
   saved=encode(r['en']);self.assertEqual(' '.join(pieces(saved,p)[1]for p in pages(saved)).split(),' '.join(pieces(rows[i],p)[1]for p in pages(rows[i])).split())
   self.assertFalse(re.search('[ぁ-ゖァ-ヺ一-鿿]',decode(rows[i])))
  body=pieces(rows[2],next(p for p in pages(rows[2])if p['flags']&1))[1]
  self.assertEqual(body.split(),"We're entering combat. All units, prepare to launch.".split())
  self.assertEqual(next(p for p in pages(rows[11])if p['flags']&1)['voice'],0)
 def test_other_pack_members_and_retained_resources_unchanged(self):
  self.assertEqual(set(self.newpacks),set(self.packs)|{4970})
  for pn,raw in self.packs.items():self.assertEqual(self.newpacks[pn],raw)
  old=(ROOT/'work/source/afs/RESOURCE/04970.bin').read_bytes();new=self.newpacks[4970]
  for a,z in zip(pack_members(old),pack_members(new)):
   self.assertEqual(a['id'],z['id'])
   if a['id']!=10511:self.assertEqual(old[a['offset']:a['offset']+a['size']],new[z['offset']:z['offset']+z['size']])
 def test_only_guarded_words_changed_and_reject_stale_inputs(self):
  masked=bytearray(self.data)
  for at in self.report['patched_words']:
   offset=self.e.offset(int(at,16));masked[offset:offset+4]=self.old[offset:offset+4]
  self.assertEqual(bytes(masked),self.old)
  self.assertEqual(len(self.report['patched_words']),32)
  with self.assertRaises(ValueError):b.patch(self.data,self.packs)

if __name__=='__main__':unittest.main()
