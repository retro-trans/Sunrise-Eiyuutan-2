"""Report explicit translation coverage; metadata only, no Japanese prose."""
import argparse
import json
import hashlib
from elf import ROOT


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    tables=json.loads((ROOT/'work/source/text_inventory.json').read_text(encoding='utf-8'))
    translated={}
    for p in (ROOT/'work/translation/en/dat').glob('*.en.json'):
        o=json.loads(p.read_text(encoding='utf-8'));translated[o['table']]={r['id']:r for r in o['rows']}
    raw_hashes=set();translated_hashes=set();details=[]
    for t in tables:
        src=json.loads((ROOT/'work/source/text'/(t['table']+'.json')).read_text(encoding='utf-8'))
        done=translated.get(t['table'],{})
        raw_hashes.update(r['sha256'] for r in src['rows'])
        translated_hashes.update(src['rows'][i]['sha256'] for i in done)
        details.append(dict(table=t['table'],stored_rows=t['rows'],drafted_rows=len(done),
                            untranslated_ids=[r['id'] for r in src['rows'] if r['id'] not in done]))
    count=sum(t['rows'] for t in tables);drafted=sum(len(v) for v in translated.values())
    library=[t for t in details if t['table'] in ('04973_10515','04973_10516')]
    ef=ROOT/'work/translation/en/elf.en.json'
    elf_drafts=len(json.loads(ef.read_text(encoding='utf-8'))['rows']) if ef.exists() else 0
    result=dict(stored_rows=count,drafted_rows=drafted,remaining_stored_rows=count-drafted,
                canonical_drafted_rows=sum('alias_of' not in r for rows in translated.values() for r in rows.values()),
                aliased_drafted_rows=sum('alias_of' in r for rows in translated.values() for r in rows.values()),
                distinct_raw_rows=len(raw_hashes),distinct_drafted_source_rows=len(translated_hashes),
                remaining_distinct_raw_rows=len(raw_hashes-translated_hashes),
                encyclopedia_rows=sum(t['stored_rows'] for t in library),encyclopedia_drafted=sum(t['drafted_rows'] for t in library),
                independently_reviewed_rows=sum(r.get('review',{}).get('accuracy')=='independent-reviewed' for rows in translated.values() for r in rows.values()),
                in_game_approved_translation_rows=sum(r.get('review',{}).get('rendered_fit')=='passed' and r.get('rendered_evidence',{}).get('draft_sha256')==hashlib.sha256(r['en'].encode('utf-8')).hexdigest() for rows in translated.values() for r in rows.values()),
                rendered_fit_builds=sorted({r['rendered_evidence']['build'] for rows in translated.values() for r in rows.values() if r.get('review',{}).get('rendered_fit')=='passed' and 'rendered_evidence' in r}),
                elf_drafted_literals=elf_drafts,total_drafted_units=drafted+elf_drafts,
                scope='ATMB only; display approvals apply to the recorded build and unchanged wording. ELF/overlay candidates, images, movies and audio need separate audits.',tables=details)
    print(json.dumps({k:v for k,v in result.items() if k!='tables'},indent=1))
    if args.write:
        dest=ROOT/'docs/coverage.json';dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(result,indent=1),encoding='utf-8')
    else:print('DRY RUN: --write saves the metadata and remaining row IDs to docs/coverage.json')


if __name__=='__main__':main()
