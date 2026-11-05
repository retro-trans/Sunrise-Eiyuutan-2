"""Regression for consecutive units reopening the exact same voiced battle line."""
import struct,sys,unittest
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[1]/'dbg')]
from walk_messages import current,prompt_ready
from message_state import ACTIVE,SPEAK_WINDOW,PARSER_CURSOR,CONTEXT,VALUE_POOL


class CaptureTests(unittest.TestCase):
    def test_identical_bark_reopened_in_new_native_window_is_not_a_duplicate(self):
        class Fake:
            def __init__(self,window):self.window=window
            def read32(self,a):return {ACTIVE:1,SPEAK_WINDOW:self.window,PARSER_CURSOR:0x1ad4981}[a]
            def read(self,a,n):
                if a==CONTEXT:
                    raw=bytearray(n);struct.pack_into('<I',raw,0,1);raw[40:43]=b'A\n\0';return bytes(raw)
                if a==VALUE_POOL:return bytes(n)
                if a==self.window:
                    win=[0]*18;win[4]=2;win[5]=15;return struct.pack('<18I',*win)
                raise AssertionError(hex(a))
        # Same cursor, voice/context and full body, different native window.
        # This reproduces the two enemy714 barks observed during tutorial32.
        first=current(Fake(0x6ab870),[13]*128)
        second=current(Fake(0x791530),[13]*128)
        self.assertIsNotNone(first);self.assertIsNotNone(second)
        self.assertNotEqual(first,second)

    def test_complete_cursor_does_not_mean_voice_gated_prompt_is_ready(self):
        class Fake:
            def __init__(self):self.enabled=0;self.xy=(0,0);self.obj=0x710000
            def read32(self,a):return {0x239594:self.obj,0x239598:self.enabled}[a]
            def read(self,a,n):
                if a==0x700018:return struct.pack('<II',118,342)
                if a==self.obj+0x18:return struct.pack('<II',*self.xy)
                raise AssertionError(hex(a))
        p=Fake();window=[0x700000]
        self.assertFalse(prompt_ready(p,window,192,28))
        p.enabled=32
        self.assertFalse(prompt_ready(p,window,192,28))
        p.xy=(310,370)
        self.assertTrue(prompt_ready(p,window,192,28))
        p.obj=0x2000000
        self.assertFalse(prompt_ready(p,window,192,28))


if __name__=='__main__':unittest.main()
