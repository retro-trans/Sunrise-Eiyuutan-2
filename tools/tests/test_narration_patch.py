"""Keep the timed opening's independent calls and complete English wording."""
import json
import unittest
from test_binary import ROOT
from message_pages import pages
from textcodec import encode, decode, parse_table
from extract import pack_members
import narration_patch as n


class NarrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.widths = bytes(json.loads((ROOT / 'work/output/v0.2.0/build_info.json').read_text())['font_widths'])

    def test_all_native_voice_function_and_blank_calls_survive(self):
        pack, layout = n.translated_pack(self.widths)
        member = next(m for m in pack_members(pack) if m['id'] == 10382)
        built = parse_table(pack[member['offset']:member['offset']+member['size']])
        source = json.loads((ROOT / 'work/source/text/04904_10382.json').read_text('utf-8'))['rows']
        totals = [0,0,0]
        for src, raw in zip(source, built):
            before, after = pages(encode(src['jp'])), pages(raw)
            self.assertEqual(len(before), len(after))
            for old, new in zip(before, after):
                self.assertEqual({k:v for k,v in old.items() if k not in ('start','end','body')},
                                 {k:v for k,v in new.items() if k not in ('start','end','body')})
                totals[0] += 1
                totals[1] += bool(new['voice'])
                totals[2] += bool(new['flags'] & 128)
        self.assertEqual(totals, [47,11,6])
        self.assertIn('\n　\n', decode(built[7]))

    def test_reflow_preserves_complete_words_and_does_not_change_authored_rows(self):
        path = ROOT / 'work/translation/en/dat/04904_10382.en.json'
        saved = path.read_bytes()
        for row in json.loads(saved)['rows']:
            staged, layout = n.stage_row(row['en'], self.widths)
            self.assertEqual(staged.split(), row['en'].split())
            self.assertTrue(all(len(p['lines']) <= 3 and max(p['widths']) <= 504 for p in layout))
        self.assertEqual(path.read_bytes(), saved)

    def test_overflow_fails_instead_of_dropping_end_of_narration(self):
        text = '\n' + 'A complete sentence. ' * 100 + '\n\n{x00}'
        with self.assertRaises(ValueError):
            n.stage_row(text, self.widths)


if __name__ == '__main__':
    unittest.main()
