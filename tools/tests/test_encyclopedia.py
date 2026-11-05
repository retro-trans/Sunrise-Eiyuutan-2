import struct,unittest
from test_binary import Cpu
from elf import Elf,PATH
import encyclopedia as e

class EncyclopediaTests(unittest.TestCase):
    def execute(self,text,table=10516):
        cpu=Cpu();cpu.put(e.BASE,e.payload(Elf(PATH.read_bytes())));source=0x700000
        cpu.put(source,text+b'\0');cpu.reg('sp',0x1800000);cpu.reg('ra',0xffff0000)
        for i,r in enumerate(('s0','s1','s2','s3','s4','s5','s6','s7')):cpu.reg(r,0x12345600+i)
        for r,v in zip(('a0','a1','a2','a3'),(5282,10824,table,11)):cpu.reg(r,v)
        pages=[];cpu.font_states=[]
        def lookup(c):
            self.assertEqual((c.reg('a0'),c.reg('a1')),(table,11));c.reg('v0',source)
        def display(c):
            self.assertEqual(tuple(c.reg(r) for r in ('a0','a1','a2','a3')),(5282,10824,table,11))
            if table in (10515,10516):
                pages.append(c.get(e.PAGE,e.PAGE_SIZE).split(b'\0')[0]);cpu.font_states.append(tuple(v-0x30 for v in struct.unpack('<2I',c.get(e.MAIL+32,8)))[::-1])
            else:pages.append(b'fallback')
            # Native calls may clobber every argument and temporary register.
            for r in ('a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7','t8','t9'):c.reg(r,0xDEADBEEF)
        cpu.run(e.WRAPPER,calls={e.GET_MESSAGE:lookup,e.CLONE:display},max_steps=500000)
        for i in range(8):self.assertEqual(cpu.reg('s'+str(i)),0x12345600+i)
        self.assertEqual(cpu.reg('sp'),0x1800000)
        return pages,cpu

    def test_pages_preserve_complete_mixed_text_and_final_word(self):
        text=b'\n@0 Title\n'+b'\n'.join((b'Line '+str(i).encode()+b' '+bytes.fromhex('82a0')) for i in range(24))+b' ending\n\n'
        pages,cpu=self.execute(text)
        self.assertEqual(len(pages),3)
        body=b''.join(p.split(b'^0,252,')[0] for p in pages)
        self.assertEqual(body.rstrip(b'\n'),text.rstrip(b'\n'))
        self.assertTrue(all(p.endswith(b'Circle: Next page') for p in pages[:-1]))
        self.assertTrue(pages[-1].endswith(b'Circle: Close'))
        self.assertIn(b'ending',pages[-1])
        self.assertEqual(struct.unpack('<I',cpu.get(e.MAIL+4,4))[0],0)
        self.assertEqual(struct.unpack('<I',cpu.get(e.MAIL+24,4))[0],0)

    def test_exact_boundary_does_not_create_blank_page(self):
        text=b'\n'.join([b'Word']*9)+b'\n\n\n'
        pages,_=self.execute(text);self.assertEqual(len(pages),1)
        self.assertTrue(pages[0].endswith(b'Circle: Close'))

    def test_other_table_uses_native_fallback(self):
        pages,_=self.execute(b'Other text',table=1233);self.assertEqual(pages,[b'fallback'])

    def test_both_buffer_bounds_fail_without_displaying_partial_text(self):
        for text,error in ((b'X'*e.FULL_SIZE,1),(b'X'*(e.PAGE_SIZE-63),2)):
            pages,cpu=self.execute(text);self.assertEqual(pages,[])
            self.assertEqual(struct.unpack('<I',cpu.get(e.MAIL+24,4))[0],error)
            self.assertEqual(struct.unpack('<I',cpu.get(e.MAIL+4,4))[0],0)
            self.assertEqual(cpu.get(e.END,16),bytes(16))

    def test_page_getter_keeps_unrelated_native_lookup(self):
        for active in (0,1):
            cpu=Cpu();cpu.put(e.GET_PAGE,e.get_page_code());cpu.put(e.MAIL+4,struct.pack('<I',active));cpu.reg('ra',0xffff0000)
            cpu.run(e.GET_PAGE,calls={0x12ca18:lambda c:c.reg('v0',0x12340000)})
            self.assertEqual(cpu.reg('v0'),e.PAGE if active else 0x12340000)

    def test_private_native_decoding_does_not_overwrite_runtime_values(self):
        cpu=Cpu();cpu.put(e.GET_MESSAGE,e.get_message_code(Elf(PATH.read_bytes())))
        old_name=bytes.fromhex('8276')*8+bytes(21);cpu.put(0x515E28,old_name)
        cpu.reg('sp',0x1800000);cpu.reg('ra',0xffff0000);cpu.reg('a0',10516);cpu.reg('a1',28)
        decoded=b'Long English description '*25
        def resource(c):self.assertEqual(c.reg('a0'),10516);c.reg('v0',0x700000)
        def label(c):self.assertEqual((c.reg('a0'),c.reg('a1')),(0x700000,28));c.reg('v0',0x710000)
        def decode(c):
            self.assertEqual(c.reg('a0'),e.CONTEXT)
            c.put(e.CONTEXT,struct.pack('<I',1));c.put(e.CONTEXT+0x28,decoded+b'\0');c.reg('v0',0x720000)
        cpu.run(e.GET_MESSAGE,calls={0x10C538:resource,0x12E958:label,0x12E9A0:decode},max_steps=1000)
        self.assertEqual(cpu.reg('v0'),e.CONTEXT+0x28)
        self.assertEqual(cpu.get(0x515E28,37),old_name)
        self.assertEqual(cpu.get(e.CONTEXT+0x28,len(decoded)),decoded)

if __name__=='__main__':unittest.main()
