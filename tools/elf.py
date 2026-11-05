"""ELF32 little-endian sections, symbols and address mapping (no fixed R addresses)."""
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'work/source/iso/SLPS_250.70'


class Elf:
    def __init__(self, data):
        self.data = data
        if data[:6] != b'\x7fELF\x01\x01':
            raise ValueError('Expected ELF32 little-endian')
        self.entry, phoff, shoff = struct.unpack_from('<III', data, 24)
        phsz, phn, shsz, shn, shstr = struct.unpack_from('<5H', data, 42)
        self.segments = [struct.unpack_from('<8I', data, phoff+i*phsz) for i in range(phn)]
        raw = [struct.unpack_from('<10I', data, shoff+i*shsz) for i in range(shn)]
        names = data[raw[shstr][4]:raw[shstr][4]+raw[shstr][5]]
        self.sections = [dict(name=names[s[0]:].split(b'\0')[0].decode('ascii'), type=s[1],
                              flags=s[2], va=s[3], offset=s[4], size=s[5], link=s[6], entsize=s[9]) for s in raw]
        self.symbols = []
        for s in self.sections:
            if s['type'] != 2:
                continue
            strings = self.sections[s['link']]
            names = data[strings['offset']:strings['offset']+strings['size']]
            for p in range(s['offset'], s['offset']+s['size'], s['entsize']):
                no, va, size, info, other, sec = struct.unpack_from('<IIIBBH', data, p)
                self.symbols.append(dict(name=names[no:].split(b'\0')[0].decode('ascii', 'replace'),
                                         va=va, size=size, type=info & 15, section=sec))

    def offset(self, va):
        for typ, off, addr, _, size, *_ in self.segments:
            if typ == 1 and addr <= va < addr+size:
                return off+va-addr
        raise ValueError('Address is not file-backed: %08X' % va)

    def at(self, va, size):
        off = self.offset(va)
        return self.data[off:off+size]

    def symbol(self, name):
        return next(s for s in self.symbols if s['name'] == name and s['section'])
