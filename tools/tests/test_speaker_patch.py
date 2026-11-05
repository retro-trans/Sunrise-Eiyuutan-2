"""Exercise relocated names through the native getter and measured VWF path."""
import json
import struct
import unittest
from test_binary import ROOT, Elf, Cpu
import speaker_patch as s
import vwf


class SpeakerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = (ROOT / 'work/output/v0.2.1/SLPS_250.70').read_bytes()
        cls.widths = bytes(json.loads((ROOT / 'work/output/v0.2.1/build_info.json').read_text())['font_widths'])
        cls.data, cls.report = s.patch_elf(cls.base, cls.widths)
        cls.elf, cls.before = Elf(cls.data), Elf(cls.base)

    def test_every_label_preserves_portrait_gameplay_and_other_name_fields(self):
        self.assertEqual(self.elf.at(s.TABLE, 64), self.before.at(s.TABLE, 64))
        for row in s.read_names():
            va = s.TABLE + row['id'] * s.STRIDE
            old, new = self.before.at(va, 64), self.elf.at(va, 64)
            if row['id'] == 1:
                self.assertEqual(old, new)
                continue
            self.assertEqual(old[:8] + old[12:], new[:8] + new[12:])
            pointer = struct.unpack_from('<I', new, 8)[0]
            self.assertEqual(self.elf.at(pointer, len(row['en']) + 1), row['en'].encode('ascii') + b'\0')
        for symbol in ('pltGetOmitName', 'pltGetPtr', 'mesSetSpeaker', 'mesDispWaistFace', 'winGTMakeDrawPacketSpknameFrameWINDOW'):
            record = self.elf.symbol(symbol)
            self.assertEqual(self.elf.at(record['va'], record['size']), self.before.at(record['va'], record['size']))

    def test_native_getter_keeps_dynamic_player_name(self):
        getter = self.elf.symbol('pltGetOmitName')
        for number in (1,6,157,566,859):
            cpu = Cpu()
            cpu.put(getter['va'], self.elf.at(getter['va'], getter['size']))
            record = s.TABLE + number * s.STRIDE
            cpu.put(record, self.elf.at(record, s.STRIDE))
            def pilot(c):
                self.assertEqual(c.reg('a0'), number)
                c.reg('v0', record)
            def player(c):
                self.assertEqual(number, 1)
                self.assertEqual(c.reg('a0'), 0)
                c.reg('v0', 0x515E28)
            cpu.reg('a0', number)
            cpu.reg('sp', 0x700000)
            cpu.reg('ra', 0xffff0000)
            cpu.run(getter['va'], calls={0x1552B0:pilot, 0x12C6A0:player})
            self.assertEqual(cpu.reg('v0'), 0x515E28 if number == 1 else struct.unpack('<I', self.elf.at(record+8,4))[0])

    def test_all_static_names_use_actual_native_width_instructions(self):
        cpu = Cpu()
        fn = self.elf.symbol('ttxtGetStrW')
        cpu.put(fn['va'], self.elf.at(fn['va'], fn['size']))
        cpu.put(0x10E058, self.elf.at(0x10E058, 0x38))  # native byte-length classifier
        cpu.put(0x108CA0, self.elf.at(0x108CA0, 0x64))  # native spacing, including halfwidth path
        cpu.put(0x108B88, self.elf.at(0x108B88, 0x10))  # native halfwidth classifier
        cpu.put(vwf.TABLE, self.elf.at(vwf.TABLE, 128))
        cpu.put(vwf.SCALE, self.elf.at(vwf.SCALE, len(vwf.scale_code())))
        # The patched native function jumps to a generated scaling wrapper.
        jump = struct.unpack('<I', self.elf.at(0x10E56C, 4))[0]
        target = (jump & 0x3ffffff) << 2
        cpu.put(target, self.elf.at(target, 20))
        for record in self.report['records']:
            if record['id'] == 1:continue
            cpu.put(0x600000, record['en'].encode('ascii') + b'\0')
            cpu.reg('a0', 0x600000)
            cpu.reg('a1', 26)
            cpu.reg('sp', 0x700000)
            cpu.reg('ra', 0xffff0000)
            cpu.run(fn['va'], max_steps=20000)
            self.assertEqual(cpu.reg('v0'), record['width_px'])
            self.assertLessEqual(cpu.reg('v0'), 540)

    def test_collision_or_changed_source_record_fails_before_output(self):
        altered = bytearray(self.base)
        altered[self.before.offset(s.TABLE + 6 * 64 + 12)] ^= 1
        with self.assertRaises(ValueError):s.patch_elf(bytes(altered), self.widths)
        altered = bytearray(self.base)
        phoff = struct.unpack_from('<I', altered,28)[0]
        phsize = struct.unpack_from('<H', altered,42)[0]
        i = next(i for i,r in enumerate(self.before.segments) if r[0] == 1 and r[2] == 0x9A0000)
        struct.pack_into('<I', altered, phoff + phsize * i + 20, 0x20000)
        with self.assertRaises(ValueError):s.patch_elf(bytes(altered), self.widths)


if __name__ == '__main__':unittest.main()
