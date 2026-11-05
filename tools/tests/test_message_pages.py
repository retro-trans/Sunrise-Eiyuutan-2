"""Compare the staging model with execution of the original GetMessagePage."""
import json,struct,unittest
from test_binary import Cpu
from elf import ROOT,PATH,Elf
from textcodec import encode
from message_pages import pages,parse_page


class MessagePageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.elf=Elf(PATH.read_bytes())

    def native(self,raw,start):
        cpu=Cpu();cpu.put(0x12e9a0,self.elf.at(0x12e9a0,0x314))
        source=0x700000;context=0x710000;cursor=0x2395ec
        cpu.put(source,raw);cpu.reg('a0',context);cpu.reg('a1',source+start)
        cpu.reg('gp',0x23f570);cpu.reg('sp',0x1800000);cpu.reg('ra',0xffff0000)
        def read(n):
            def call(c):
                p=struct.unpack('<I',c.get(cursor,4))[0]
                if n=='sjis':
                    first=c.get(p,1)[0];size=2 if 0x81<=first<=0x9f or 0xe0<=first<=0xfc else 1
                    value=int.from_bytes(c.get(p,size),'big')
                else:size=n;value=int.from_bytes(c.get(p,n),'little')
                c.put(cursor,struct.pack('<I',p+size));c.reg('v0',value)
            return call
        def put(c):
            n=2 if c.reg('a1')&0xff00 else 1;p=c.reg('a0')
            c.put(p,(c.reg('a1')&0xffff).to_bytes(n,'big'));c.reg('v0',p+n)
        cpu.run(0x12e9a0,calls={0x12e838:read('sjis'),0x12e880:read(2),0x12e8a8:read(4),0x12e8f8:put},max_steps=20000)
        head=struct.unpack('<10I',cpu.get(context,40));body=cpu.get(context+40,2000).split(b'\0')[0]
        return dict(start=start,end=cpu.reg('v0')-source,flags=head[0],speaker=head[1],voice=head[2],
                    voice_parameter=head[3],function=head[4],arguments=list(head[6:6+head[5]]),body=body)

    def test_all_opening_story_calls_match_original_machine_code(self):
        source=json.loads((ROOT/'work/source/text/04905_10383.json').read_text(encoding='utf-8'))['rows']
        self.assertEqual(len(source),49);calls=0
        for row in source:
            raw=encode(row['jp'])
            for page in pages(raw):
                with self.subTest(row=row['id'],offset=page['start']):self.assertEqual(page,self.native(raw,page['start']))
                calls+=1
        self.assertGreater(calls,202)

    def test_line_start_and_binary_payloads_do_not_create_false_pages(self):
        raw=b'\n'+bytes.fromhex('81930100819582960a0000000000')+b'Rate'+bytes.fromhex('819382f0')+b'\n\n\0'
        for page in pages(raw):self.assertEqual(page,self.native(raw,page['start']))
        self.assertEqual(pages(raw)[1]['voice'],10)
        self.assertIn(bytes.fromhex('819382f0'),pages(raw)[1]['body'])

    def test_current_english_story_calls_match_original_machine_code(self):
        from story_layout import wrap_row
        translation=json.loads((ROOT/'work/translation/en/dat/04905_10383.en.json').read_text(encoding='utf-8'))['rows']
        widths=json.loads((ROOT/'work/output/v0.1.69/build_info.json').read_text())['font_widths']
        self.assertEqual(len(translation),49);calls=0;bodies=0
        for row in translation:
            text,report=wrap_row(row['en'],widths,centered_calls={33:(3,),40:(1,)}.get(row['id'],()))
            raw=encode(text);bodies+=len(report)
            for page in pages(raw):
                with self.subTest(row=row['id'],offset=page['start']):self.assertEqual(page,self.native(raw,page['start']))
                calls+=1
        self.assertEqual((calls,bodies),(368,215))

    def test_control_only_function_and_formatting_are_preserved(self):
        raw=bytes.fromhex('819582860100010056000000')+b'\n'+bytes.fromhex('819782830400819782960000819782830000')+b'\n\n\0'
        for page in pages(raw):self.assertEqual(page,self.native(raw,page['start']))
        self.assertEqual(pages(raw)[0]['arguments'],[86])
        self.assertEqual(pages(raw)[0]['body'],b'')
        self.assertEqual(pages(raw)[1]['body'],b'%4@0%0\n')

    def test_first_battle_original_and_wrapped_english_match_native_parser(self):
        from story_layout import wrap_row
        source=json.loads((ROOT/'work/source/text/04949_10472.json').read_text(encoding='utf-8'))['rows']
        draft=json.loads((ROOT/'work/translation/en/dat/04949_10472.en.json').read_text(encoding='utf-8'))['rows']
        widths=json.loads((ROOT/'work/output/v0.1.70/build_info.json').read_text())['font_widths']
        self.assertEqual((len(source),len(draft)),(42,42));calls=bodies=0
        for s,d in zip(source,draft):
            self.assertEqual(s['id'],d['id'])
            text,report=wrap_row(d['en'],widths,profile='battle-tutorial');bodies+=len(report)
            for raw in (encode(s['jp']),encode(text)):
                for page in pages(raw):
                    with self.subTest(row=s['id'],offset=page['start']):self.assertEqual(page,self.native(raw,page['start']))
                    calls+=1
        self.assertEqual((calls,bodies),(492,140))

    def test_unproven_or_truncated_records_are_rejected(self):
        for raw in (b'No terminator',bytes.fromhex('819301'),bytes.fromhex('8195828601000500')+bytes(20)+b'\0',bytes.fromhex('819782830a00')+b'\0'):
            with self.assertRaises(ValueError):pages(raw)


if __name__=='__main__':unittest.main()
