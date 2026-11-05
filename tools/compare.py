"""Compare local source assets/text with Sunrise R; never import translations."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from elf import ROOT,PATH,Elf


def normal(text):
    text=re.sub(r'\{[^}]*\}|%[A-Za-z0-9]','',text)
    return re.sub(r'\s+','',unicodedata.normalize('NFKC',text))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    sibling=ROOT.parent/'Sunrise Eiyuutan'
    rrows=[r for p in (sibling/'work/source/text').glob('*.json') for r in json.loads(p.read_text(encoding='utf-8'))['rows']]
    tables=[json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'work/source/text').glob('*.json')]
    newrows=[r for t in tables for r in t['rows']]
    rtext={normal(r['jp']) for r in rrows if normal(r['jp'])}
    newtext={normal(r['jp']) for r in newrows if normal(r['jp'])}
    matched=newtext&rtext
    rassets={}
    for p in (sibling/'work/source/dat').glob('*/*.bin'):
        h=hashlib.sha256(p.read_bytes()).hexdigest();rassets.setdefault(h,[]).append(str(p.relative_to(sibling)))
    index=json.loads((ROOT/'work/source/resource_index.json').read_text(encoding='utf-8'))
    shared=[]
    for pack in index:
        for m in pack['members']:
            if m['sha256'] in rassets:
                shared.append(dict(pack=pack['pack'],member=m['id'],sha256=m['sha256'],r_paths=rassets[m['sha256']]))
    newelf=Elf(PATH.read_bytes());relf=(sibling/'work/source/iso/SLPS_250.11').read_bytes();code=[]
    for name in ['fontSjisToJis','fontChgASCIItoJIS','fontChkCodeASCII']:
        s=newelf.symbol(name);body=newelf.at(s['va'],s['size']);off=relf.find(body)
        code.append(dict(function=name,eiyuutan2_va=hex(s['va']),exact_r_file_offset=hex(off) if off>=0 else None))
    result=dict(r_table_rows=len(rrows),eiyuutan2_table_rows=len(newrows),
                eiyuutan2_unique_raw_rows=len({r['sha256'] for r in newrows}),
                unique_normalized_text=dict(r=len(rtext),eiyuutan2=len(newtext),shared=len(matched)),
                shared_asset_occurrences=len(shared),shared_unique_asset_hashes=len({r['sha256'] for r in shared}),
                code=code,shared_assets=shared)
    print(json.dumps({k:v for k,v in result.items() if k!='shared_assets'},indent=1))
    if args.write:
        (ROOT/'work/source/comparison.json').write_text(json.dumps(result,indent=1),encoding='utf-8')
    else:print('DRY RUN: --write saves hash/path evidence without script prose')


if __name__=='__main__':main()
