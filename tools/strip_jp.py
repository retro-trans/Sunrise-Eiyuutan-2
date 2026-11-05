"""Prepare English-only, source-hashed translation copies; --write saves them.

The review status records this pass, not independent approval or in-game fit.
"""
import argparse
import json
import re
import hashlib
from elf import ROOT,Elf,PATH
from textcodec import controls
from battle_bank import alias_exports


def review_status(row):
    result=dict(accuracy='self-reviewed',editorial='self-reviewed',proofread='self-reviewed',rendered_fit='pending')
    for key,value in row.get('review',{}).items():
        if key not in result:
            raise ValueError('Invalid review metadata')
        allowed=('pending','passed') if key=='rendered_fit' else ('self-reviewed','independent-reviewed','pending')
        if value not in allowed:raise ValueError('Invalid review stage value')
        result[key]=value
    return result


def attach_fit_evidence(clean,row):
    if clean['review']['rendered_fit']!='passed':return
    evidence=row.get('rendered_evidence')
    if not isinstance(evidence,dict):raise ValueError('Passed display fit needs versioned evidence')
    if evidence.get('draft_sha256')!=hashlib.sha256(row['en'].encode('utf-8')).hexdigest():
        clean['review']['rendered_fit']='pending'
        return # Wording changes expire earlier display approval.
    required=('build','draft_sha256','built_row_sha256','native_sha256','pages','audit','build_elf_sha256')
    if any(k not in evidence for k in required) or not re.fullmatch(r'0\.\d+\.\d+',evidence['build']) or evidence['pages']<1:
        raise ValueError('Incomplete display-fit evidence')
    clean['rendered_evidence']={k:evidence[k] for k in required}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true');args=ap.parse_args()
    prepared={}
    for p in sorted((ROOT/'work/translation/en/dat').glob('*.json')):
        if p.name.endswith('.en.json'):continue
        draft=json.loads(p.read_text(encoding='utf-8'));name=draft['table']
        source=json.loads((ROOT/'work/source/text'/(name+'.json')).read_text(encoding='utf-8'))
        rows=[];seen=set()
        for row in draft['rows']:
            i=row['id'];en=row['en'];src=source['rows'][i]
            if i in seen:raise ValueError('Duplicate ID')
            seen.add(i)
            if controls(src['jp'])!=controls(en):raise ValueError('Control mismatch '+name+':'+str(i))
            if re.search(r'[\u3040-\u30ff\u3400-\u9fff\uff61-\uff9f]',en):raise ValueError('Japanese in English')
            clean=dict(id=i,en=en,source_sha256=src['sha256'],status='reviewed-draft',
                       review=review_status(row))
            if row.get('notes'):
                if re.search(r'[\u3040-\u30ff\u3400-\u9fff\uff61-\uff9f]',row['notes']):raise ValueError('Japanese notes cannot enter an English export')
                clean['notes']=row['notes']
            attach_fit_evidence(clean,row)
            rows.append(clean)
        result=dict(table=name,rows=rows)
        if p.stem!=name or name in prepared:raise ValueError('Duplicate or mismatched canonical table')
        prepared[name]=result
    prepared.update(alias_exports(prepared))
    extra={p.name.removesuffix('.en.json') for p in (ROOT/'work/translation/en/dat').glob('*.en.json')}-prepared.keys()
    if extra:raise ValueError('Unexpected/stale generated exports: '+str(sorted(extra)))
    for name,result in sorted(prepared.items()):
        dest=ROOT/f'work/translation/en/dat/{name}.en.json'
        print(name,'rows',len(result['rows']),'sample',ascii(result['rows'][0]['en'][:130]))
        if args.write:dest.write_text(json.dumps(result,ensure_ascii=False,indent=1),encoding='utf-8')
        if args.check:
            saved=json.loads(dest.read_text(encoding='utf-8'))
            if saved!=result:raise ValueError('Stale English export')
    p=ROOT/'work/translation/en/elf.json'
    if p.exists():
        elf=Elf(PATH.read_bytes());rows=[]
        for row in json.loads(p.read_text(encoding='utf-8'))['rows']:
            raw=elf.at(row['va'],row['source_size'])
            if elf.at(row['va']+row['source_size'],1)!=b'\0':raise ValueError('ELF string boundary')
            if len(row['en'].encode('ascii'))>len(raw):raise ValueError('ELF literal needs relocation')
            if re.findall(rb'%[a-zA-Z]',raw)!=re.findall(rb'%[a-zA-Z]',row['en'].encode('ascii')):raise ValueError('Printf mismatch')
            clean={**row,'source_sha256':hashlib.sha256(raw).hexdigest(),'status':'reviewed-draft',
                   'review':review_status(row)}
            clean.pop('rendered_evidence',None);attach_fit_evidence(clean,row);rows.append(clean)
        result=dict(rows=rows);dest=p.with_name('elf.en.json')
        print('ELF rows',len(rows),'sample',ascii(rows[0]['en']))
        if args.write:dest.write_text(json.dumps(result,indent=1),encoding='utf-8')
        if args.check and json.loads(dest.read_text(encoding='utf-8'))!=result:raise ValueError('Stale ELF export')
    if not args.write and not args.check:print('DRY RUN: --write creates English-only files; --check verifies saved copies')


if __name__=='__main__':main()
