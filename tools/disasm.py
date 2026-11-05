"""Read-only symbol-aware disassembly. R5900-only opcodes may appear as raw words."""
import argparse
import struct
import capstone
from elf import PATH,Elf


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--elf',default=str(PATH));ap.add_argument('--symbol')
    ap.add_argument('--range',nargs=2,metavar=('START','END'));ap.add_argument('--symbols',action='store_true');args=ap.parse_args()
    elf=Elf(open(args.elf,'rb').read())
    if args.symbols:
        for s in sorted(elf.symbols,key=lambda s:s['va']):
            if s['section'] and s['va']:print('%08X %06X %s'%(s['va'],s['size'],s['name']))
        return
    if args.symbol:
        s=elf.symbol(args.symbol);start,end=s['va'],s['va']+s['size']
    elif args.range:start,end=(int(v,16) for v in args.range)
    else:ap.error('--symbol, --symbols, or --range is required')
    md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS64|capstone.CS_MODE_LITTLE_ENDIAN);md.skipdata=True
    for va in range(start,end,4):
        raw=elf.at(va,4);ins=next(md.disasm(raw,va),None)
        label=ins.mnemonic+' '+ins.op_str if ins and ins.mnemonic!='.byte' else '.word 0x%08X'%struct.unpack('<I',raw)[0]
        print('%08X %s  %s'%(va,raw.hex(),label))


if __name__=='__main__':main()
