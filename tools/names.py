"""Audit glossary names; replace only explicitly registered English variants.

Default is a dry run. Run after meaning fixes, then regenerate English exports.
Approved en/expanded forms are the reviewers' do-not-touch list. Never infer an
English name from a similar Japanese term or copy a similar translated row.
"""
import argparse,json,re
from elf import ROOT

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    glossary=json.loads((ROOT/'work/glossary/glossary.json').read_text(encoding='utf-8'))
    aliases={};approved=set()
    for entry in glossary['entries']:
        approved.add(entry['en'])
        if entry.get('expanded'):approved.add(entry['expanded'])
        for alias in entry.get('english_variants',[]):
            if alias in aliases and aliases[alias]!=entry['en']:raise ValueError('Ambiguous English glossary variant')
            aliases[alias]=entry['en']
    if any(alias in approved for alias in aliases):raise ValueError('Variant conflicts with approved form')
    paths=sorted((ROOT/'work/translation/en/dat').glob('*.json'))
    paths=[p for p in paths if not p.name.endswith('.en.json')]+[ROOT/'work/translation/en/elf.json']
    examined=0;changes=[]
    for p in paths:
        if not p.exists():continue
        obj=json.loads(p.read_text(encoding='utf-8'));dirty=False
        for row in obj['rows']:
            examined+=1;old=row['en'];new=old
            for alias,target in sorted(aliases.items(),key=lambda pair:-len(pair[0])):
                new=re.sub(r'(?<!\w)'+re.escape(alias)+r'(?!\w)',lambda m:target,new)
            if new!=old:
                changes.append(dict(file=p.name,id=row['id'],before=old,after=new));row['en']=new;dirty=True
        if args.write and dirty:p.write_text(json.dumps(obj,ensure_ascii=False,indent=1),encoding='utf-8')
    print(json.dumps(dict(examined_rows=examined,registered_variants=len(aliases),changed_rows=len(changes),samples=changes[:4],do_not_touch=sorted(approved)),ensure_ascii=True,indent=1))
    if not args.write:print('DRY RUN: --write applies registered English variants only.')
if __name__=='__main__':main()
