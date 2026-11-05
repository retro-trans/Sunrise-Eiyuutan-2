import struct,unittest
from test_binary import Cpu
from elf import Elf,PATH
import preview
from unittest.mock import patch

class PreviewTests(unittest.TestCase):
    def test_runtime_test_name_bounds(self):
        self.assertEqual(len(preview.name_bytes(chr(0xFF37)*8)),37)
        self.assertEqual(preview.name_bytes(chr(0xFF37)*8)[:16],bytes.fromhex('8276')*8)
        for bad in ('','A'*9,'Bad\nName','Bad@Name'):
            with self.assertRaises(ValueError):preview.name_bytes(bad)

    def test_runtime_name_only_writes_owned_slot_in_active_copied_entry(self):
        class Fake:
            def __init__(self):self.writes=[]
            def read(self,addr,size):
                if addr==0x12C620:return bytes.fromhex('b0ffbd273000b3ff')
                if addr==preview.NAME_SLOT:return b'O'+bytes(36)
                if addr==0x70002C:return struct.pack('<f',128.0)
                raise AssertionError(addr)
            def read32(self,addr):
                if addr==0x237BF8:return 0x700000
                if addr==0x51D71C:return 0
                raise AssertionError(addr)
            def write(self,addr,data):self.writes.append((addr,data))
        p=Fake()
        with patch('preview.status',return_value=dict(running=1,pagination=dict(active=1))):
            self.assertEqual(preview.set_test_name(p,'Test'),b'O'+bytes(36))
        self.assertEqual(p.writes,[(preview.NAME_SLOT,b'Test'+bytes(33))])
        with patch('preview.status',return_value=dict(running=1,pagination=dict(active=0))):
            with self.assertRaises(RuntimeError):preview.set_test_name(p,'Test')
        self.assertEqual(len(p.writes),1)

    def test_initial_request_bounds(self):
        for kind in preview.TABLES:
            with self.assertRaises(ValueError):preview.initial(kind,-1)
            with self.assertRaises(ValueError):preview.initial(kind,preview.TABLES[kind][1])

    def test_descriptor_coverage_and_explicit_fallback_guard(self):
        elf=Elf(PATH.read_bytes());fallbacks=preview.descriptor_fallbacks(elf)
        self.assertEqual(len(fallbacks),1)
        f=fallbacks[0]
        self.assertEqual((f['table'],f['row'],f['source_row'],f['descriptor_address'],f['resource_pack'],f['cg_asset']),
                         (10515,134,125,0x1C3B50,5100,10642))
        with patch.dict(preview.DESCRIPTOR_FALLBACKS,{'pilot':{}}):
            with self.assertRaisesRegex(ValueError,'Unexpected missing pilot'):preview.descriptor_fallbacks(elf)
        class Duplicate:
            def at(self,base,size):
                raw=bytearray(elf.at(base,size));raw[20:24]=raw[4:8];return raw
        with self.assertRaisesRegex(ValueError,'Invalid native pilot'):preview.descriptor_fallbacks(Duplicate())

    def test_unlisted_hana_uses_earlier_art_but_later_text(self):
        elf=Elf(PATH.read_bytes());cpu=Cpu();cpu.put(preview.DRIVER,preview.driver_code())
        cpu.put(preview.MAIL,preview.initial('pilot',134))
        for _,(_,_,base,records) in preview.TABLES.items():cpu.put(base,elf.at(base,records*16))
        cpu.reg('ra',0xffff0000);cpu.reg('sp',0x1800000)
        for i in range(5):cpu.reg('s'+str(i),0xabcdef00+i)
        seen=[]
        def display(c):
            seen.append(tuple(c.reg(r) for r in ('a0','a1','a2','a3')))
            c.put(preview.MAIL+8,struct.pack('<I',308))
        cpu.run(preview.DRIVER,calls={0x13ffa0:display},max_steps=10000)
        self.assertEqual(seen,[(5100,10642,10515,134)])
        self.assertEqual(struct.unpack('<I',cpu.get(preview.MAIL+20,4))[0],1)
        self.assertEqual(struct.unpack('<I',cpu.get(preview.MAIL+24,4))[0],0)
        self.assertEqual(cpu.reg('sp'),0x1800000)
        for i in range(5):self.assertEqual(cpu.reg('s'+str(i)),0xabcdef00+i)

    def test_original_initialization_precedes_library(self):
        cpu=Cpu();cpu.put(preview.ENTRY,preview.entry_code());cpu.reg('ra',0xffff0000);cpu.reg('sp',0x1800000)
        calls=[]
        cpu.run(preview.ENTRY,calls={0x102530:lambda c:calls.append('init'),0x13f5d8:lambda c:calls.append('library')})
        self.assertEqual(calls,['init','library']);self.assertEqual(cpu.reg('sp'),0x1800000)

    def test_native_row_lookup_switch_and_bounded_exit(self):
        elf=Elf(PATH.read_bytes());cpu=Cpu();cpu.put(preview.DRIVER,preview.driver_code())
        cpu.put(preview.MAIL,preview.initial('machine',279));expected={}
        for kind,(table,count,base,records) in preview.TABLES.items():
            raw=elf.at(base,records*16);cpu.put(base,raw)
            for pos in range(0,len(raw),16):
                _,label,res,cg=struct.unpack_from('<4I',raw,pos);expected[(table,label)]=(res,cg)
        cpu.reg('ra',0xffff0000);cpu.reg('sp',0x1800000)
        for i in range(5):cpu.reg('s'+str(i),0xabcdef00+i)
        seen=[]
        def display(c):
            key=(c.reg('a2'),c.reg('a3'));seen.append(key)
            self.assertEqual((c.reg('a0'),c.reg('a1')),expected[key])
            if len(seen)==1:c.put(preview.MAIL+4,struct.pack('<II',10515,307))
            else:c.put(preview.MAIL+8,struct.pack('<I',0xffffffff))
        cpu.run(preview.DRIVER,calls={0x13ffa0:display},max_steps=10000)
        self.assertEqual(seen,[(10516,279),(10515,307)])
        self.assertEqual(struct.unpack('<I',cpu.get(preview.MAIL+24,4))[0],0)
        self.assertEqual(struct.unpack('<I',cpu.get(preview.MAIL+20,4))[0],2)
        for i in range(5):self.assertEqual(cpu.reg('s'+str(i)),0xabcdef00+i)

if __name__=='__main__':unittest.main()
