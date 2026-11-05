import unittest
from test_binary import ROOT
from textcodec import decode,encode,controls
import layout,encyclopedia as e
import test_encyclopedia as ep


class FontCommandTests(unittest.TestCase):
    def test_renderer_records_are_lossless_and_binary_payload_stays_opaque(self):
        raw=b'\n#5Long heading#2\nNormal\0'
        text=decode(raw)
        self.assertEqual(controls(text),['{C:2335}','{C:2332}','{x00}'])
        self.assertEqual(encode(text),raw)
        binary=bytes.fromhex('81958296233500000000')
        self.assertEqual(controls(decode(binary)),['{C:81958296233500000000}'])
        self.assertEqual(encode(decode(binary)),binary)

    def test_modes_measure_native_scaled_advances_and_runtime_expansion(self):
        widths=bytes([13]*128)
        self.assertEqual(layout.width('{C:2335}AB{C:2332}AB',widths),46)
        self.assertEqual(layout.width('{C:2335}{C:819782960000}',widths),120)
        self.assertEqual(layout.width('{C:2335}'+chr(0xff37),widths),15)
        self.assertEqual(layout.width(chr(0xff37),widths),28)
        with self.assertRaises(ValueError):layout.width('{C:2330}A',widths)

    def test_wrap_carries_mode_across_inserted_and_original_newlines(self):
        widths=bytes([13]*128);text='{C:2335}AAAA BBBB CCCC DDDD{C:2332} End'
        wrapped=layout.wrap(text,widths,80)
        self.assertEqual(wrapped,'{C:2335}AAAA BBBB\nCCCC DDDD{C:2332}\nEnd')
        self.assertEqual(layout.line_widths(wrapped,widths),[72,72,45])
        self.assertEqual(controls(wrapped),controls(text))
        self.assertEqual(layout.line_widths('{C:2335}A\nB{C:2332}\nC',widths),[8,8,15])

    def test_native_pages_restore_carried_mode_and_keep_footer_normal(self):
        text=b'#5'+b'\n'.join([b'Compressed text']*15)+b'#2\nNormal ending\n'
        pages,cpu=ep.EncyclopediaTests().execute(text)
        self.assertEqual(cpu.font_states,[(2,5),(5,2)])
        self.assertIn(b'#2^0,252,Circle: Next page',pages[0])
        self.assertTrue(pages[1].startswith(b'#5'))
        restored=b''.join(e.source_page_body(p.split(b'^0,252,')[0],*state) for p,state in zip(pages,cpu.font_states))
        self.assertEqual(restored,text)
        self.assertEqual(controls(decode(restored)),['{C:2335}','{C:2332}'])

    def test_final_compressed_page_resets_footer_without_losing_source_control(self):
        text=b'#5Compressed ending\n'
        pages,cpu=ep.EncyclopediaTests().execute(text)
        self.assertEqual(cpu.font_states,[(2,5)])
        body=pages[0].split(b'^0,252,')[0]
        self.assertTrue(body.endswith(b'#2'))
        self.assertEqual(e.source_page_body(body,2,5),text)
        with self.assertRaises(ValueError):e.source_page_body(body[:-2],2,5)
        with self.assertRaises(ValueError):e.source_page_body(b'Lost prefix#2',5,5)


if __name__=='__main__':unittest.main()
