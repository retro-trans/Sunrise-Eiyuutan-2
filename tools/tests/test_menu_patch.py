"""Guard relocation space and preserve native two-byte name editing choices."""
import string
import struct
import unittest
from test_binary import ROOT, Elf
import menu_patch as m


class MenuPatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = (ROOT / 'work/output/v0.1.139/SLPS_250.70').read_bytes()
        cls.patched, cls.report = m.patch_elf(cls.baseline)

    def test_every_latin_letter_retains_both_native_cell_forms(self):
        elf = Elf(self.patched)
        table = int(self.report['choices_table'], 16)
        for i, letter in enumerate(string.ascii_uppercase):
            address = struct.unpack('<I', elf.at(table + i * 4, 4))[0]
            choice = elf.at(address, 5)
            self.assertEqual(choice[-1], 0)
            self.assertEqual(choice[:4].decode('cp932'), m.fullwidth(letter + letter.lower()))
        pointer = struct.unpack('<I', elf.at(table + 51 * 4, 4))[0]
        self.assertEqual(pointer, 0x231370)  # Keep the complete native symbol inventory.
        self.assertEqual(elf.at(pointer, 256), Elf(self.baseline).at(pointer, 256))

    def test_default_name_fits_eight_native_cells_and_stays_terminated(self):
        elf = Elf(self.patched)
        address = int(self.report['default_name_va'], 16)
        name = elf.at(address, 11)
        self.assertEqual(name[-1], 0)
        self.assertEqual(name[:-1].decode('cp932'), m.fullwidth('Kanji'))
        self.assertLessEqual(len(name[:-1]) // 2, 8)

    def test_occupied_reservation_is_refused(self):
        data = bytearray(self.baseline)
        elf = Elf(data)
        i, s = next((i, s) for i, s in enumerate(elf.segments) if s[2] == 0x9A0000)
        phoff = struct.unpack_from('<I', data, 28)[0]
        phsize = struct.unpack_from('<H', data, 42)[0]
        struct.pack_into('<I', data, phoff + phsize * i + 20, 0x20000)
        with self.assertRaises(AssertionError):
            m.patch_elf(bytes(data))

    def test_altered_title_overlay_is_refused_without_partial_output(self):
        title = (ROOT / 'work/source/afs/EVEMAP/00001.bin').read_bytes()
        patched = m.patch_title(title)
        self.assertEqual(len(title), len(patched))
        with self.assertRaises(ValueError):
            m.patch_title(patched)
        bad = bytearray(title)
        bad[0x7B7] ^= 1
        with self.assertRaises(ValueError):
            m.patch_title(bytes(bad))


if __name__ == '__main__':
    unittest.main()
