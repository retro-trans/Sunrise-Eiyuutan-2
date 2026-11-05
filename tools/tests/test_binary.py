"""Binary safety regressions, including execution of the generated MIPS hooks."""
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import vwf
from elf import ROOT,PATH,Elf
from build import replace_pack,inputs
from extract import pack_members
from textcodec import decode,encode,parse_table,build_table
import layout
from extract import strings
from afs import validate_partition
import control


class Cpu:
    """Small test interpreter for the integer instructions emitted by vwf.py.
    Models branch delay slots explicitly; this is not a PS2 emulator.
    """
    def __init__(self):self.r=[0]*32;self.mem={};self.lo=0
    def put(self,a,b):self.mem.update({a+i:v for i,v in enumerate(b)})
    def get(self,a,n):return bytes(self.mem.get(a+i,0) for i in range(n))
    def reg(self,name,value=None):
        i=vwf.R[name]
        if value is not None:self.r[i]=value
        return self.r[i]
    def run(self,pc,stop=0xFFFF0000,calls=None,max_steps=200):
        pending=None
        for _ in range(max_steps):
            if pc==stop:return
            if calls and pc in calls:
                calls[pc](self);pc=self.reg('ra');continue
            w=struct.unpack('<I',self.get(pc,4))[0];op=w>>26;rs=(w>>21)&31;rt=(w>>16)&31;rd=(w>>11)&31;sa=(w>>6)&31;fn=w&63;im=w&65535;si=im-65536 if im&32768 else im
            jump=None;skip_delay=False;v=self.r[rs];t=self.r[rt]
            if op==0:
                if fn in (0x21,0x2d):self.r[rd]=(v+t)&0xffffffffffffffff
                elif fn in (0x23,0x2f):self.r[rd]=(v-t)&0xffffffffffffffff
                elif fn==0:self.r[rd]=(t<<sa)&0xffffffff
                elif fn==2:self.r[rd]=(t&0xffffffff)>>sa
                elif fn==3:self.r[rd]=((t&0x7fffffff)-(t&0x80000000))>>sa
                elif fn==0x3c:self.r[rd]=(t<<(sa+32))&0xffffffffffffffff
                elif fn==0x3f:self.r[rd]=((t&0x7fffffffffffffff)-(t&0x8000000000000000))>>(sa+32)
                elif fn==8:jump=v
                elif fn==9:jump=v;self.r[rd]=pc+8
                elif fn==0xa:
                    if not t:self.r[rd]=v
                elif fn==0xb:
                    if t:self.r[rd]=v
                elif fn==0x25:self.r[rd]=v|t
                elif fn==0x24:self.r[rd]=v&t
                elif fn==0x27:self.r[rd]=~(v|t)&0xffffffffffffffff
                elif fn==0x2b:self.r[rd]=int(v<t)
                elif fn==0x2a:self.r[rd]=int(((v&0x7fffffff)-(v&0x80000000))<((t&0x7fffffff)-(t&0x80000000)))
                elif fn==0x18:self.lo=v*t;self.r[rd]=self.lo&0xffffffff
                elif fn==0x1a:self.lo=v//t
                elif fn==0x1b:self.lo=(v&0xffffffff)//(t&0xffffffff)
                elif fn==0x12:self.r[rd]=self.lo
                else:raise AssertionError(hex(w))
            elif op in (2,3):
                jump=((pc+4)&0xf0000000)|((w&0x3ffffff)<<2)
                if op==3:self.r[31]=pc+8
            elif op in (4,5):
                taken=(v==t) if op==4 else (v!=t)
                if taken:jump=pc+4+si*4
            elif op==6:
                if ((v&0x7fffffff)-(v&0x80000000))<=0:jump=pc+4+si*4
            elif op==1 and rt==1:
                if not v&0x80000000:jump=pc+4+si*4
            elif op in (0x14,0x15):
                taken=(v==t) if op==0x14 else (v!=t)
                if taken:jump=pc+4+si*4
                else:skip_delay=True
            elif op==0xf:self.r[rt]=im<<16
            elif op==0x1c and fn==0x18:self.r[rd]=(v*t)&0xffffffff
            elif op==0xb:self.r[rt]=int(v<si%(1<<64))
            elif op==0xa:self.r[rt]=int(((v&0x7fffffff)-(v&0x80000000))<si)
            elif op==9:self.r[rt]=(v+si)&0xffffffff
            elif op==0x19:self.r[rt]=(v+si)&0xffffffffffffffff
            elif op==0xd:self.r[rt]=v|im
            elif op==0xe:self.r[rt]=v^im
            elif op==0xc:self.r[rt]=v&im
            elif op in (0x20,0x21,0x23,0x24,0x25,0x37):
                n={0x20:1,0x21:2,0x23:4,0x24:1,0x25:2,0x37:8}[op];self.r[rt]=int.from_bytes(self.get(v+si,n),'little')
                if op==0x20 and self.r[rt]&0x80:self.r[rt]|=0xffffffffffffff00
                if op==0x21 and self.r[rt]&0x8000:self.r[rt]|=0xffffffffffff0000
            elif op in (0x1a,0x1b,0x2c,0x2d):
                addr=v+si;k=addr&7;base=addr&~7;rb=bytearray((t&0xffffffffffffffff).to_bytes(8,'little'))
                if op==0x1a:rb[7-k:]=self.get(base,k+1);self.r[rt]=int.from_bytes(rb,'little')
                elif op==0x1b:rb[:8-k]=self.get(addr,8-k);self.r[rt]=int.from_bytes(rb,'little')
                elif op==0x2c:self.put(base,rb[7-k:])
                else:self.put(addr,rb[:8-k])
            elif op in (0x28,0x2b,0x29,0x3f):
                n={0x28:1,0x2b:4,0x29:2,0x3f:8}[op];self.put(v+si,(t% (1<<(n*8))).to_bytes(n,'little'))
            else:raise AssertionError(hex(w))
            self.r[0]=0
            if pending is not None:
                if jump is not None:raise AssertionError('Branch in delay slot')
                pc=pending;pending=None
            else:pc+=8 if skip_delay else 4;pending=jump
        raise AssertionError('Hook did not return')


class BinaryTests(unittest.TestCase):
    def test_sampling_reset_does_not_report_false_progress(self):
        class Fake:
            def __init__(self,values):self.values=iter(values)
            def read32(self,addr):return next(self.values)
        with self.assertRaises(RuntimeError):control.frames(Fake([1000,10]),2)
        control.frames(Fake([1000,1002]),2)

    def test_partition_rejects_appended_out_of_order_files(self):
        good=[dict(offset=2048,size=2048),dict(offset=4096,size=2048)]
        validate_partition(good)
        with self.assertRaises(ValueError):validate_partition([dict(offset=8192,size=2048),good[1]])

    def test_cached_sizes_follow_growing_resource_packs(self):
        data,packs,report=inputs();elf=Elf(data);original=Elf(PATH.read_bytes())
        base=elf.symbol('_pacfileA')['va']
        for pn,pack in packs.items():
            flag,size=struct.unpack('<II',elf.at(base+pn*8,8))
            self.assertEqual(size,len(pack))
            self.assertEqual(flag,struct.unpack('<I',original.at(base+pn*8,4))[0])

    def test_scanner_keeps_mixed_ascii_single_kanji_and_halfwidth(self):
        for text in ['PlayStation 2 \u5c02\u7528','\u529b','\uff71']:
            rows=list(strings(text.encode('cp932')+b'\0'))
            self.assertEqual(rows[0]['jp'],text)

    def test_wrap_preserves_words_controls_and_runtime_width(self):
        widths=bytes([13]*128)
        text='\n{C:819782960000} Akatsuki\nThis complete sentence must survive word wrapping.\n{x00}'
        wrapped=layout.wrap(text,widths,504)
        self.assertEqual(wrapped.split(),text.split())
        self.assertTrue(all(layout.width(line,widths)<=504 for line in wrapped.split('\n')))
        self.assertEqual(layout.width('{C:819782960000}',widths),224)
        with self.assertRaises(ValueError):layout.wrap('W'*100,widths)

    def test_control_nulls_and_duplicate_cp932(self):
        data=b'\n\x81\x93\x00\x00\x81\x95\x82\x96\x59\x02\0\0\0\0Hello\0'
        self.assertEqual(encode(decode(data)),data)
        self.assertIn('{C:81930000}',decode(data))
        for bad in [b'\x81\x93',b'\x81\x95\x82\x96\x00']:
            with self.assertRaises(ValueError):decode(bad)

    def test_all_shipped_tables(self):
        tables=rows=0
        for p in (ROOT/'work/source/afs/RESOURCE').glob('*.bin'):
            d=p.read_bytes()
            for m in pack_members(d):
                b=d[m['offset']:m['offset']+m['size']]
                if b[:4]!=b'ATMB':continue
                parts=parse_table(b);self.assertEqual(build_table(parts),b);tables+=1;rows+=len(parts)
                for raw in parts:self.assertEqual(encode(decode(raw)),raw)
        self.assertEqual((tables,rows),(51,15154))

    def test_resource_noop_and_growth(self):
        d=(ROOT/'work/source/afs/RESOURCE/00023.bin').read_bytes()
        self.assertEqual(replace_pack(d,{}),d)
        member=next(m for m in pack_members(d) if m['id']==1233)
        raw=d[member['offset']:member['offset']+member['size']]
        grown=raw+b'\0'*12345
        result=replace_pack(d,{1233:grown});members=pack_members(result)
        self.assertTrue(all(a['offset']+a['size']<=b['offset'] for a,b in zip(members,members[1:])))
        for m in members:
            old=next(o for o in pack_members(d) if o['id']==m['id'])
            expected=grown if m['id']==1233 else d[old['offset']:old['offset']+old['size']]
            self.assertEqual(result[m['offset']:m['offset']+m['size']],expected)

    def test_generated_scale_all_ascii_and_sizes(self):
        widths=bytes([13]*32+[5]+[4+(c%19) for c in range(33,128)])
        for code in list(range(128))+[0x8140,0x8296,0xffff]:
            for full in [13,20,26,52,78]:
                c=Cpu();c.put(vwf.TABLE,widths);c.put(vwf.SCALE,vwf.scale_code())
                c.reg('a0',code);c.reg('a1',full);c.reg('ra',0xffff0000);c.reg('s0',0x12345678)
                c.run(vwf.SCALE)
                self.assertEqual(c.reg('v0'),vwf.scaled_width(code,full,widths))
                self.assertEqual(c.reg('s0'),0x12345678);self.assertEqual(c.reg('a0'),code)

    def test_optional_font_outputs(self):
        widths=bytes([13]*32+[5]+[8]*95)
        for code in [0,32,65,127,0x8140]:
            for wp,hp in [(0,0),(0x4000,0),(0,0x4010),(0x4000,0x4010)]:
                c=Cpu();c.put(vwf.TABLE,widths);c.put(0x108c40,vwf.font_wh())
                for k,v in [('a0',code),('a1',wp),('a2',hp),('ra',0xffff0000)]:c.reg(k,v)
                c.run(0x108c40)
                self.assertEqual(c.reg('v0'),26)
                if wp:self.assertEqual(int.from_bytes(c.get(wp,4),'little'),widths[code] if code<128 else 26)
                if hp:self.assertEqual(int.from_bytes(c.get(hp,4),'little'),26)
                self.assertNotIn(0,c.mem)

    def test_input_hook_delay_slot(self):
        payload,patches=vwf.patches(PATH.read_bytes())
        _,_,hook,_=next(p for p in patches if p[0]==0x1044b0)
        c=Cpu();c.put(0x1044b0,hook);c.put(vwf.MONITOR+0x100,vwf.monitor_code())
        c.put(vwf.MONITOR+4,struct.pack('<I',32));c.reg('v1',0xff00);c.reg('v0',255);c.reg('s0',0x4000)
        c.run(0x1044b0,stop=0x1044b8)
        self.assertEqual(c.get(0x4000,2),b'\x20\0')
        self.assertEqual(int.from_bytes(c.get(vwf.MONITOR+8,4),'little'),1)


if __name__=='__main__':unittest.main()
