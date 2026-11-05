"""Execute ending-clock control paths and validate complete movie replacements."""
import json,struct,unittest
from elf import ROOT,Elf
import movie_patch as b
import movie_lyrics_native as n
from test_binary import Cpu

class MovieTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=(ROOT/'work/output/v0.2.18/SLPS_250.70').read_bytes();cls.before=Elf(cls.base);cls.d,cls.jp,_=b.language();cls.data,cls.report=b.patch_ending(cls.base,cls.d,cls.jp);cls.e=Elf(cls.data)
 def cpu(self):
  c=Cpu();c.put(n.BASE,self.e.at(n.BASE,n.LIMIT-n.BASE))
  for start,end in b.POOLS[1:]:c.put(start,self.e.at(start,end-start))
  c.reg('sp',0x500000);c.reg('ra',0xffff0000);c.reg('v0',0x1234)
  for i,r in enumerate(('s0','s1','s2','s3')):c.reg(r,0x1234567800000000+i)
  c.put(n.PCM,struct.pack('<IHHIII',1,5,1,0,0,0x610000));return c
 def calls(self,c,sample=0,status=3,rate=48000):
  seen=[];allocated=[0x620000,0x630000]
  def create(m):
   win=allocated[len([x for x in seen if x[0]=='create'])%2];m.put(win+8,bytes(4));m.reg('v0',win);seen.append(('create',win,m.reg('t1'),m.reg('t3')))
  def clock(m):m.put(m.reg('a1'),struct.pack('<I',sample));m.put(m.reg('a2'),struct.pack('<I',rate))
  def draw(m):seen.append(('draw',m.reg('a0'),m.reg('a1'),m.reg('t0'),m.reg('a3')))
  return {0x186FB0:lambda m:m.reg('v0',status),0x1870A8:clock,0x1112F8:create,0x1523A0:lambda m:seen.append(('clear',m.reg('a0'))),0x110EA0:draw,0x10EF50:lambda m:seen.append(('delete',m.reg('a0')))},seen
 def run_code(self,c,sample=0,**kwargs):
  calls,seen=self.calls(c,sample,**kwargs);c.run(n.BASE,calls=calls,max_steps=1500)
  self.assertEqual(c.reg('sp'),0x500000);self.assertEqual(c.reg('v0'),0x1234)
  for i,r in enumerate(('s0','s1','s2','s3')):self.assertEqual(c.reg(r),0x1234567800000000+i)
  return seen
 def test_all34_complete_cues_follow_the_actual_sample_clock(self):
  for index,cue in enumerate(self.d['ending']['cues'],1):
   c=self.cpu();seen=self.run_code(c,round((cue['start']+cue['end'])/2*48000));self.assertEqual(len([s for s in seen if s[0]=='create']),2)
   table=struct.unpack('<5I',self.e.at(n.TABLE+(index-1)*20,20));draw=[s for s in seen if s[0]=='draw'];self.assertEqual([s[2]for s in draw],list(table[2:]));self.assertEqual([s[3:]for s in draw],[(22,0),(17,52),(20,0)])
   self.assertEqual(int.from_bytes(c.get(n.STATE+8,4),'little'),index);self.assertEqual(self.run_code(c,table[0]),[])
 def test_instrumental_gap_hides_both_windows_and_next_cue_reuses_them(self):
  c=self.cpu();self.run_code(c,48000);self.assertFalse(self.run_code(c,20*48000))
  for win in(0x620000,0x630000):self.assertTrue(int.from_bytes(c.get(win+8,4),'little')&0x80000000)
  seen=self.run_code(c,31*48000);self.assertFalse(any(s[0]=='create'for s in seen));self.assertEqual(len([s for s in seen if s[0]=='draw']),3)
  for win in(0x620000,0x630000):self.assertFalse(int.from_bytes(c.get(win+8,4),'little')&0x80000000)
 def test_other_music_voice_and_invalid_clock_never_create_caption_windows(self):
  for off,value,length in((0,0,4),(4,4,2),(6,2,2)):
   c=self.cpu();c.put(n.PCM+off,value.to_bytes(length,'little'));self.assertEqual(self.run_code(c),[])
  self.assertEqual(self.run_code(self.cpu(),status=5),[]);self.assertEqual(self.run_code(self.cpu(),rate=1),[])
 def test_stop_deletes_once_and_clears_persistent_state(self):
  c=self.cpu();self.run_code(c,48000);c.put(n.PCM,bytes(4));seen=self.run_code(c);self.assertEqual(seen,[('delete',0x620000),('delete',0x630000)]);self.assertEqual(c.get(n.STATE,12),bytes(12));self.assertEqual(self.run_code(c),[])
 def test_hook_original_delay_slot_and_all_other_prior_bytes_preserved(self):
  c=self.cpu();c.put(n.HOOK,self.e.at(n.HOOK,8));c.reg('sp',0x500000-0x70);calls,seen=self.calls(c);c.run(n.HOOK,calls=calls,max_steps=1500);self.assertEqual(c.reg('sp'),0x500000)
  out=bytearray(self.data)
  for va,size in[(n.HOOK,4),(n.BASE,n.LIMIT-n.BASE),*[(s,t-s)for s,t in b.POOLS[1:]]]:out[self.before.offset(va):self.before.offset(va)+size]=self.base[self.before.offset(va):self.before.offset(va)+size]
  self.assertEqual(bytes(out),self.base)
 def test_all40_video_payloads_keep_exact_audio_and_original_extents(self):
  import movie_pss,re
  for m in self.d['movies']:
   raw,report=b.movie_bytes(m);video,audio=movie_pss.streams(raw);self.assertEqual(b.digest(video),report['video_sha256']);self.assertEqual(b.digest(audio),report['original_adx_sha256']);self.assertEqual(movie_pss.ipu_header(video)[2:],(m['width'],m['height'],m['frames']))
   starts=[16]+[q.end()for q in re.finditer(b'\x00\x00\x01\xb0',video)][:-1];self.assertEqual(len(starts),m['frames']);self.assertTrue(all(video[q]&0x20 for q in starts),'Every frame must retain the native-compatible intra VLC format1')
   self.assertLessEqual(max(map(len,movie_pss.frames(video))),30000,'A picture must fit the original32KiB refill envelope')
 def test_clock_avoids_the_games_zero_time_platform_stub(self):
  from mips import pack,sw,ori,jr
  self.assertEqual(self.before.at(0x18E7E0,16),pack([sw('zero',0,'a1'),ori('v0','zero',48000),jr('ra'),sw('v0',0,'a2')]))
 def test_opening_audio_and_picture_delivery_remain_within_bounded_lookahead(self):
  import movie_pss,bisect
  m=next(m for m in self.d['movies']if m['member']==488);raw,_=b.movie_bytes(m);video,audio=movie_pss.streams(raw);ends=[];n=16
  for pic in movie_pss.frames(video):n+=len(pic);ends.append(n)
  start=int.from_bytes(audio[2:4],'big')+4;block=audio[5]*audio[7];rate=int.from_bytes(audio[8:12],'big');vp=ap=0
  for x,y,kind,sub,body in movie_pss.packets(raw):
   if sub==0xc0:vp+=y-body
   elif sub==0x90:ap+=y-body
   else:continue
   vt=bisect.bisect_right(ends,vp)/30;at=max(0,ap-start)/block*32/rate
   self.assertLessEqual(abs(vt-at),1.0,'Fixed old byte-slot muxing must not return: it accumulates seconds of delivery drift')

if __name__=='__main__':unittest.main()
