"""Real native Information consumers and complete measured item columns."""
import json,re,struct,unittest
from elf import ROOT,PATH,Elf
from test_binary import Cpu
from layout import width
import information_patch as b

class InformationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=(ROOT/'work/output/v0.2.16/SLPS_250.70').read_bytes();cls.before=Elf(cls.base);cls.source=Elf(PATH.read_bytes());cls.data,cls.report=b.patch(cls.base);cls.e=Elf(cls.data);cls.d=b.language();cls.widths=bytes(json.loads((ROOT/'work/output/v0.2.16/build_info.json').read_text('utf8'))['font_widths'])
 def address(self,va):return int(self.report['addresses'][hex(va)],16)
 def text(self,c,va):
  out=bytearray()
  while c.get(va+len(out),1)!=b'\0':out.extend(c.get(va+len(out),1))
  return out.decode('cp932')
 def cpu(self):
  c=Cpu();c.put(b.BASE,b.code());c.reg('sp',0x500000);c.reg('ra',0xffff0000);return c
 def test_complete228_objects_and183_typed_records(self):
  self.assertEqual((len(self.d['rows']),len(self.d['records']),len(self.d['fields'])),(228,183,732))
  for r in self.d['rows']:
   raw=r['en'].encode('cp932')+b'\0';self.assertEqual(self.e.at(self.address(r['va']),len(raw)),raw);self.assertNotIn('jp',r);self.assertIsNone(re.search('[ぁ-ゖァ-ヺ一-鿿]',r['en']))
   self.assertEqual(self.e.at(r['va'],r['source_size']),self.source.at(r['va'],r['source_size']))
  fields={r['site']:r for r in self.d['fields']}
  for r in self.d['records']:
   raw=bytearray(self.e.at(r['va'],r['size']))
   for off in range(0,r['size'],4):
    if r['va']+off in fields:
     f=fields[r['va']+off];self.assertEqual(int.from_bytes(raw[off:off+4],'little'),self.address(f['target']));raw[off:off+4]=f['target'].to_bytes(4,'little')
   self.assertEqual(bytes(raw),self.source.at(r['va'],r['size']))
 def test_actual_info_top_dispatch_produces_english_all_four_headers(self):
  for selected,label in enumerate(('Allies','Units','Battleships','Items'),1):
   c=self.cpu();c.put(0x13F390,self.e.at(0x13F390,0x248));c.put(0x1C5830,self.e.at(0x1C5830,16));c.reg('a0',selected);seen=[]
   def sprintf(m):
    fmt=m.reg('a1');ptr=m.reg('a2');self.assertEqual(self.e.at(fmt,len('Information  %s')+1),b'Information  %s\0');self.assertEqual(self.e.at(ptr,len(label)+1),label.encode()+b'\0');seen.append(label)
   c.run(0x13F390,calls={0x19F1C0:sprintf,0x13F6C8:lambda m:None,0x1305A8:lambda m:None},max_steps=200)
   self.assertEqual(seen,[label]);self.assertEqual(c.reg('v0'),selected)
 def test_real_initial_scan_uses_pixels_and_fixed_item_buffer_width(self):
  for texts,wanted in [(['WWWW','iiiiii'],'WWWW'),(['\x1fAir-to-Ground Missile Cannon\t1','\x1fEN Charger\t23'],None)]:
   c=self.cpu();c.put(0x13F714,self.e.at(0x13F714,0x60));context=0x600000;c.reg('s0',context);c.reg('s2',0);c.reg('s3',0);c.reg('s6',0);c.put(context+4,struct.pack('<3I',0,len(texts),0x700000));pointers=[]
   for i,t in enumerate(texts):ptr=0x710000+i*0x100;pointers.append(ptr);c.put(ptr,t.encode()+b'\0')
   def name(m):m.reg('v0',pointers[m.reg('a0')])
   def measure(m):m.reg('v0',width(self.text(m,m.reg('a0')),self.widths))
   c.run(0x13F714,stop=0x13F774,calls={0x700000:name,0x10E510:measure},max_steps=300)
   self.assertEqual(c.reg('v0'),608 if wanted is None else width(wanted,self.widths))
 def test_actual_item_formatter_keeps_complete_name_and_signed_quantity(self):
  for qty in(-128,0,1,21,127):
   c=self.cpu();c.put(0x13FC40,self.e.at(0x13FC40,0x7C));fmt=int(self.report['format_va'],16);c.put(fmt,b.FORMAT.encode()+b'\0');c.put(0x700000,b'Air-to-Ground Missile Cannon\0');c.reg('a0',0x5D5)
   def sprintf(m):
    self.assertEqual(self.text(m,m.reg('a1')),b.FORMAT);q=(m.reg('a3')&0x7fffffff)-(m.reg('a3')&0x80000000);m.put(m.reg('a0'),(b.FORMAT%(self.text(m,m.reg('a2')),q)).encode()+b'\0')
   def strlen(m):m.reg('v0',len(self.text(m,m.reg('a0')).encode()))
   c.run(0x13FC40,calls={0x156858:lambda m:m.reg('v0',0x700000),0x13A3B8:lambda m:m.reg('v0',qty),0x19F1C0:sprintf,0x19F7D8:strlen})
   self.assertEqual(self.text(c,c.reg('v0')),'\x1fAir-to-Ground Missile Cannon\t'+str(qty))
 def test_complete_columns_draw_without_marker_and_restore_owned_text(self):
  for text in ('\x1fName\tOwned','\x1fAir-to-Ground Missile Cannon\t1','\x1fS-EN Charger\t21','\x1fEnhanced Armor\t-128','\x1fImproved Ultra-Compact Nuclear Fusion Engine\t127'):
   c=self.cpu();raw=text.encode()+b'\0';c.put(0x700000,raw);c.reg('s0',0x1234);c.reg('s1',0x5678)
   for r,v in [('a0',0x600000),('a1',0x700000),('a2',0),('a3',17),('t0',26),('t1',26),('t2',4)]:c.reg(r,v)
   seen=[]
   def draw(m):seen.append((self.text(m,m.reg('a1')),m.reg('a2'),m.reg('a3'),m.reg('t0'),m.reg('t1'),m.reg('t2')))
   def measure(m):m.reg('v0',width(self.text(m,m.reg('a0')),self.widths))
   c.run(b.RENDER,calls={0x110EA0:draw,0x10E510:measure},max_steps=1000)
   name,qty=text[1:].split('\t');font=22 if width(name,self.widths)>520 else 26;self.assertEqual(seen,[(name,8,17,font,26,4),(qty,600-width(qty,self.widths),17,26,26,4)]);self.assertEqual(c.get(0x700000,len(raw)),raw);self.assertEqual((c.reg('s0'),c.reg('s1'),c.reg('sp')),(0x1234,0x5678,0x500000))
 def test_unmarked_renderer_and_header_wrapper_preserve_original_arguments(self):
  for entry,original in((b.RENDER,0x110EA0),(b.DEFAULT_RENDER,0x110E98)):
   c=self.cpu();c.put(0x700000,b'Ordinary prior label\0');args={'a0':0x600000,'a1':0x700000,'a2':3,'a3':4,'t0':5,'t1':6,'t2':7}
   for r,v in args.items():c.reg(r,v)
   seen=[];c.run(entry,calls={original:lambda m:seen.append({r:m.reg(r)for r in args})});self.assertEqual(seen,[args])
 def test_real_selstr_constructor_owns_complete_copy_and_fixed_width(self):
  c=self.cpu();c.put(0x1127A8,self.e.at(0x1127A8,0x90));raw=b'\x1fAir-to-Ground Missile Cannon\t127\0';c.put(0x700000,raw);c.reg('a0',0x700000);c.reg('a1',26);c.reg('a2',26);alloc=iter((0x600000,0x610000))
  def malloc(m):m.reg('v0',next(alloc))
  def strcpy(m):m.put(m.reg('a0'),self.text(m,m.reg('a1')).encode()+b'\0')
  c.run(0x1127A8,calls={0x110FF0:malloc,0x19F7D8:lambda m:m.reg('v0',len(raw)-1),0x19F6C4:strcpy})
  self.assertEqual(c.reg('v0'),0x600000);self.assertEqual(c.get(0x610000,len(raw)),raw);self.assertEqual(struct.unpack('<5I',c.get(0x600000,20)),(0x610000,26,26,608,28));self.assertEqual(c.get(0x700000,len(raw)),raw)
 def test_actual_native_row_keeps_id_scroll_height_and_zero_center_offset(self):
  c=self.cpu();c.put(0x13F8CC,self.e.at(0x13F8CC,0x54));c.reg('s0',0x600000);c.put(0x600004,struct.pack('<I',1));c.reg('s1',0x610000);c.reg('s2',7);c.reg('s3',84);c.reg('s5',304);c.reg('s6',608);c.reg('s7',28);c.reg('v0',0x700000);seen=[]
  def create(m):seen.append((m.reg('t3'),m.reg('t2'),m.reg('a2'),m.reg('a3')));m.reg('v0',0x620000);m.put(0x62000c,struct.pack('<I',0x630000));m.put(0x63000c,struct.pack('<I',608))
  c.run(0x13F8CC,stop=0x13F920,calls={0x112868:create})
  self.assertEqual(seen,[(8,84,26,26)]);self.assertEqual(struct.unpack('<4I',c.get(0x62001c,16)),(608,28,0,0));self.assertEqual(c.reg('s3'),112)
 def test_all_item_names_descriptions_fit_and_controls_survive(self):
  for r in self.d['layout']:
   size=r['font_width'];metric=lambda s:sum((self.widths[ord(c)]*size//26 if ord(c)<128 else size)+2 for c in s);self.assertEqual(r['widths'],[metric(x)for x in r['lines']]);self.assertLessEqual(max(r['widths'],default=0),r['limit'],r['id'])
  for r in self.d['reflow']:self.assertEqual(r['before'].split(),r['after'].split())
  for r in self.d['rows']:
   old=self.source.at(r['va'],r['source_size'])[:-1].decode('cp932');self.assertEqual(re.findall(r'[-+]\d+',old),re.findall(r'[-+]\d+',r['en']),r['id'])
 def test_all_unrelated_loaded_bytes_and_prior_language_are_retained(self):
  changed={int(k,16)for k in self.report['patched_words']}
  for seg in self.before.segments:
   if seg[0]!=1:continue
   va,n=seg[2],seg[4];old=self.before.at(va,n);new=bytearray(self.e.at(va,n))
   for p in changed:
    if va<=p<va+n:new[p-va:p-va+4]=old[p-va:p-va+4]
   for start,size in[(b.BASE,len(b.code()))]+[(int(p['va'],16),p['size'])for p in self.report['payloads']]:
    if va<=start<va+n:new[start-va:start-va+size]=bytes(size)
   self.assertEqual(bytes(new),old)
  with self.assertRaises(ValueError):b.patch(self.data)
  with self.assertRaises(ValueError):b.patch(PATH.read_bytes())
 def test_equipment_picker_measures_full_names_and_preserves_arguments(self):
  for profile in self.d['picker_layout']:
   c=self.cpu();text=profile['formatted'];c.put(0x700000,text.encode('cp932')+b'\0');args={'a0':0x600000,'a1':0x700000,'a2':18,'a3':26,'t0':4,'t1':5,'t2':6,'t3':7}
   for reg,v in args.items():c.reg(reg,v)
   def measure(m):m.reg('v0',sum((self.widths[ord(x)]*18//26 if ord(x)<128 else 18)+2 for x in self.text(m,m.reg('a0'))))
   seen=[];c.run(b.FIT_PICKER,calls={0x10E510:measure,0x112868:lambda m:seen.append({r:m.reg(r)for r in args})})
   self.assertEqual(seen,[dict(args,a2=profile['font_width'])]);self.assertEqual(c.reg('sp'),0x500000)
 def test_scoped_removal_modal_measures_pixels_and_keeps_native_choices(self):
  for name in ('Enhanced Armor','Improved Ultra-Compact Nuclear Fusion Engine'):
   c=self.cpu();text='['+name+']\nRemove this equipment?';c.put(0x700000,text.encode()+b'\0');c.reg('a0',9);c.reg('a1',0x700000);created=[];drawn=[]
   c.put(0x9bb810,b'Yes\0');c.put(0x9bb818,b'No\0')
   def create(m):
    ptr=0x600000+len(created)*0x100;created.append(tuple(m.reg(r)for r in ('t0','t1','t2','t3')));m.reg('v0',ptr);m.put(ptr+0x1c,struct.pack('<3I',created[-1][1],created[-1][2],created[-1][3]))
   def measure(m):m.reg('v0',width(self.text(m,m.reg('a0')),self.widths))
   c.run(b.REMOVE,calls={0x10E510:measure,0x1112f8:create,0x1523b8:lambda m:drawn.append(self.text(m,m.reg('a1'))),0x111bb0:lambda m:None,0x113ca8:lambda m:None,0x113a78:lambda m:m.reg('v0',1),0x111c90:lambda m:None,0x10ef50:lambda m:None},max_steps=2000)
   w=max(width(line,self.widths)for line in text.splitlines())+16
   self.assertEqual(created[0],((640-w)//2,(448-76)//2,w,76));self.assertLessEqual(w,608);self.assertEqual(drawn,[*text.splitlines(),'Yes','No']);self.assertEqual(c.reg('v0'),1);self.assertEqual(c.reg('sp'),0x500000)
 def test_equipment_formats_preserve_words_arguments_and_fit_status_panel(self):
  for mode in (0,2):
   c=self.cpu();c.put(0x12CF68,self.e.at(0x12CF68,28));c.put(0x700000,('#'+str(mode)).encode()+b'\0');c.reg('s0',0x700000);c.reg('s1',0x600000);c.reg('v0',35);c.reg('v1',35);c.run(0x12CF68,stop=0x12D06C);self.assertEqual(int.from_bytes(c.get(0x600010,4),'little'),mode)
  for f in self.d['format_overrides']:
   self.assertEqual(f['proposed_en'],'#0'+f['current_v016_en']+'#2')
   for pair in f['reference_pairs']:
    high=int.from_bytes(self.e.at(pair['lui_va'],4),'little')&65535;low=int.from_bytes(self.e.at(pair['low_va'],4),'little')&65535;ptr=(high<<16)+(low-65536 if low&32768 else low);raw=f['proposed_en'].encode()+b'\0';self.assertEqual(self.e.at(ptr,len(raw)),raw)
  names={r['va']:r['en']for r in self.d['rows']};metric=lambda s:sum((self.widths[ord(x)]*13//26 if ord(x)<128 else 13)+2 for x in s)
  for record in self.d['records']:
   if record['table']!='it_mchdev_info':continue
   fields={x['offset']:x['target']for x in self.d['fields']if x['table']==record['table']and x['row']==record['row']};name=names[fields[8]];desc=names[fields[12]]
   lines=[name,'Atk[AT999 EN999] Def[DF999  EN 999]',*desc.split('\n')];self.assertLessEqual((len(lines)-1)*15+13,84);self.assertLessEqual(max(map(metric,lines)),504);self.assertLessEqual(metric('Equipment 1:'+name),504)

if __name__=='__main__':unittest.main()
