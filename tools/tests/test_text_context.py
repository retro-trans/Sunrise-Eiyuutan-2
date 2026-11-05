"""Native header-position regressions: punctuation must not swallow prose."""
import json
import unittest
from test_binary import ROOT, Cpu
from elf import Elf, PATH
from textcodec import decode, encode, controls


class TextContextTests(unittest.TestCase):
    def test_header_parameter_and_midline_percent_are_distinct(self):
        raw = b'\n' + bytes.fromhex('81930000') + b'Rate100' + bytes.fromhex('819382f0') + b'\n\0'
        text = decode(raw)
        self.assertEqual(controls(text), ['{C:81930000}', '{x00}'])
        self.assertIn('Rate100\uff05\u3092', text)
        self.assertEqual(encode(text), raw)
        with self.assertRaises(ValueError):
            decode(bytes.fromhex('8193'))
        self.assertEqual(decode(b'A' + bytes.fromhex('8193')), 'A\uff05')

    def test_other_header_prefixes_are_visible_after_body_text(self):
        for value, glyph in (('8190', '\uff04'), ('8195', '\uff06')):
            raw = b'Body' + bytes.fromhex(value) + b'End\0'
            self.assertEqual(decode(raw), 'Body' + glyph + 'End{x00}')
            self.assertEqual(encode(decode(raw)), raw)
        header = bytes.fromhex('81900000') + b'Body\0'
        self.assertEqual(controls(decode(header)), ['{C:81900000}', '{x00}'])

    def test_binary_payload_does_not_change_line_state(self):
        # Real record widths; payloads deliberately contain LF, NUL and percent.
        voice = bytes.fromhex('819582960a8193000000')
        function = bytes.fromhex('81958286010002000a819382f0000000')
        for record in (voice, function):
            raw = record + bytes.fromhex('81930000') + b'Body\0'
            self.assertEqual(controls(decode(raw)),
                             ['{C:' + record.hex().upper() + '}', '{C:81930000}', '{x00}'])
            self.assertEqual(encode(decode(raw)), raw)

    def test_only_native_body_advancing_records_end_header_state(self):
        tail = bytes.fromhex('819382f0')
        for prefix in (b'#5', bytes.fromhex('819782960000'),
                       bytes.fromhex('819782620100'), bytes.fromhex('818f0a')):
            self.assertIn('\uff05\u3092', decode(prefix + tail))
            self.assertEqual(encode(decode(prefix + tail)), prefix + tail)
        for prefix in (bytes.fromhex('819782930500'), bytes.fromhex('819782970100'),
                       bytes.fromhex('819782830100')):
            self.assertEqual(controls(decode(prefix + bytes.fromhex('81930000')))[-1], '{C:81930000}')
        self.assertIn('{C:81930000}', decode(b'Body\n' + bytes.fromhex('81930000')))

    def test_real_native_header_gate_skips_parameter_read_in_body(self):
        elf = Elf(PATH.read_bytes())
        start, end = 0x12EA38, 0x12EA68
        for position in (0, 1, 20):
            cpu = Cpu()
            cpu.put(start, elf.at(start, end-start))
            cpu.reg('v0', 0x8193)
            cpu.reg('s4', position)
            cpu.reg('s3', 0x700000)
            cpu.reg('ra', 0xffff0000)
            calls = []
            def read_parameter(c):
                calls.append('u16 parameter')
                c.reg('v0', 0x1234)
            def body(c):
                calls.append('body path')
                c.reg('ra', 0xffff0000)
            cpu.run(start, stop=0x12EC58 if not position else 0xffff0000,
                    calls={0x12E880: read_parameter, 0x12EB2C: body}, max_steps=30)
            self.assertEqual(calls, ['u16 parameter'] if not position else ['body path'])
            if not position:
                self.assertEqual(int.from_bytes(cpu.get(0x700004, 4), 'little'), 0x1234)
                self.assertEqual(int.from_bytes(cpu.get(0x700000, 4), 'little'), 0x10)

    def test_both_library148_source_rows_expose_visible_percent_particle(self):
        for table in ('04973_10515', '04973_10516'):
            row = json.loads((ROOT/'work/source/text'/(table+'.json')).read_text(encoding='utf-8'))['rows'][148]
            raw = encode(row['jp'])
            text = decode(raw)
            self.assertIn('\uff05\u3092', text)
            self.assertNotIn('{C:819382F0}', text)
            self.assertEqual(encode(text), raw)


if __name__ == '__main__':
    unittest.main()
