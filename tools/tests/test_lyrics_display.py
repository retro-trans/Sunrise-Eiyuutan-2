"""Exercise the new two-tier ending code and unchanged cue/media boundaries."""
import json,re,struct,unittest
from elf import ROOT,Elf
import lyrics_display_patch as b
import movie_lyrics_native as n
import test_movie_subtitles as original

class LyricsDisplayTests(unittest.TestCase):
 cpu=original.MovieTests.cpu
 calls=original.MovieTests.calls
 run_code=original.MovieTests.run_code
 @classmethod
 def setUpClass(cls):
  cls.base=(ROOT/'work/output/v0.2.22/SLPS_250.70').read_bytes();cls.data,cls.report=b.patch(cls.base);cls.e=Elf(cls.data);cls.d,_,_=b.movies.language()
 def test_all34_cues_draw_only_romaji_and_english_at_original_times(self):
  before=Elf(self.base)
  self.assertEqual(self.e.at(n.TABLE,34*20),before.at(n.TABLE,34*20))
  for i,cue in enumerate(self.d['ending']['cues']):
   c=self.cpu();table=struct.unpack('<5I',self.e.at(n.TABLE+i*20,20));seen=self.run_code(c,(table[0]+table[1])//2)
   self.assertEqual([s[2]for s in seen if s[0]=='draw'],list(table[3:]))
   self.assertEqual([s[3:]for s in seen if s[0]=='draw'],[(17,0),(20,0)])
   self.assertEqual([s[2:]for s in seen if s[0]=='create'],[(8,48),(376,64)])
   self.assertFalse(self.run_code(c,table[1]-1))
 def test_gap_reuse_and_stop_cleanup_with_two_tiers(self):
  c=self.cpu();self.run_code(c,48000);self.assertFalse(self.run_code(c,20*48000))
  for win in(0x620000,0x630000):self.assertTrue(int.from_bytes(c.get(win+8,4),'little')&0x80000000)
  seen=self.run_code(c,31*48000);self.assertEqual(len([s for s in seen if s[0]=='draw']),2);self.assertFalse(any(s[0]=='create'for s in seen))
  for win in(0x620000,0x630000):self.assertFalse(int.from_bytes(c.get(win+8,4),'little')&0x80000000)
  c.put(n.PCM,bytes(4));self.assertEqual(self.run_code(c),[('delete',0x620000),('delete',0x630000)]);self.assertFalse(self.run_code(c))
 def test_only_ending_helper_changes_in_complete_v022_elf(self):
  e=Elf(self.base);out=bytearray(self.data);off=e.offset(n.BASE);size=self.report['previous_code_size'];out[off:off+size]=self.base[off:off+size];self.assertEqual(bytes(out),self.base)
  original.MovieTests.test_other_music_voice_and_invalid_clock_never_create_caption_windows(self)
 def test_all21_opening_cues_retain_exact_romanization_english_and_times(self):
  m,ass=b.opening();_,jp,_=b.movies.language();old=b.captions.movie_ass(m,jp['cues']);events=lambda s:[x for x in s.splitlines()if x.startswith('Dialogue:')]
  expected=[x.replace(r'\pos(320,42)',r'\pos(320,10)')for x in events(old)if r'\fs20}'not in x]
  self.assertEqual(events(ass),expected);self.assertEqual(len(events(ass)),42);self.assertFalse(re.search('[\u3040-\u30ff\u3400-\u9fff]',ass))
 def test_new_opening_preserves_original_audio_extent_frames_and_safe_format(self):
  m,_=b.opening();raw,report=b.movie_bytes(m);video,audio=b.movie_pss.streams(raw)
  self.assertEqual(b.digest(video),report['video_sha256']);self.assertEqual(b.digest(audio),report['original_adx_sha256']);self.assertEqual(b.movie_pss.ipu_header(video)[2:],(m['width'],m['height'],m['frames']))
  self.assertEqual(len(b.movie_pss.frames(video)),2752)

if __name__=='__main__':unittest.main()
