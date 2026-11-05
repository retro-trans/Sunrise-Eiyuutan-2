"""Inventory verified ATMB tables; --write saves source rows and resource manifests."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
from elf import ROOT
from extract import pack_members
from textcodec import decode, encode, parse_table, build_table


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    tables=[]; index=[]; magic=collections.Counter()
    for p in sorted((ROOT/'work/source/afs/RESOURCE').glob('*.bin')):
        data=p.read_bytes(); members=pack_members(data)
        for m in members:
            blob=data[m['offset']:m['offset']+m['size']]
            m['magic']=blob[:4].hex(); m['sha256']=hashlib.sha256(blob).hexdigest()
            magic[m['magic']]+=1
            if blob[:4]!=b'ATMB': continue
            name='%05d_%05d'%(int(p.stem),m['id'])
            rawrows=parse_table(blob)
            assert build_table(rawrows)==blob, name+' table roundtrip'
            rows=[]
            for i,raw in enumerate(rawrows):
                text=decode(raw)
                assert encode(text)==raw, '%s row %d codec roundtrip'%(name,i)
                rows.append(dict(id=i,jp=text,size=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
            tables.append(dict(table=name,pack=int(p.stem),member=m['id'],rows=len(rows),
                               bytes=len(blob),sha256=m['sha256'],unique_rows=len(set(rawrows))))
            if args.write:
                dest=ROOT/'work/source/text'/(name+'.json');dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_text(json.dumps(dict(table=name,rows=rows),ensure_ascii=False,indent=1),encoding='utf-8')
        index.append(dict(pack=int(p.stem),members=members))
    summary=dict(tables=len(tables),rows=sum(t['rows'] for t in tables),
                 packs=len(index),members=sum(len(p['members']) for p in index),types=magic)
    print(json.dumps(summary,indent=1))
    for t in tables: print(t['table'],t['rows'],t['bytes'])
    if args.write:
        for name,obj in [('text_inventory.json',tables),('resource_index.json',index)]:
            (ROOT/'work/source'/name).write_text(json.dumps(obj,indent=1),encoding='utf-8')
    else: print('DRY RUN: all table and codec roundtrips verified; --write saves local catalogs')


if __name__=='__main__':main()
