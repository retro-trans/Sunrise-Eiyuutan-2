"""Source-gated battle-bank insertion and explicit identical-source aliases.

Language is stored once in the canonical working draft. Alias exports preserve
reviewed language but never inherit a different physical destination's fit proof.
"""
import copy,hashlib,json,re
from pathlib import Path
from elf import ROOT
from extract import pack_members
from textcodec import parse_table,encode,controls
from message_pages import pages

CANONICAL='00022_10512'
ALIAS='04971_11849'
TABLES=(CANONICAL,ALIAS)
SOURCE_SHA='9ab4d059047dfc4f2f208eeafae5e265e2aa71f6cb214e2882a57511c627c6cf'
SOURCE_ROWS=6519
# Original, individually inspected speaker-only records. The absent voice cue is
# intentional input data, not permission to accept arbitrary unvoiced staging.
# See docs/battle_unvoiced_source79.json for original parser/code evidence.
UNVOICED_SOURCES={
    195:'dd607c75e42fbd3565747d102fcd2e0fc2e949217eb52f4e06604edd31104a18',
    196:'fd09c7d249a9f904a4269ad2d5942955732d41d7df86f1d18235bc4347da76dc',
    197:'82568869e91c4658e9595af6719e6f1f9bf7f053e63796a49d46bcc7588c9810',
    198:'327485b9eabcc9d17a973648203c6db890b6a101f60c48bb17f357ec9c731d67',
    199:'03b98245a7259c1033d1827be90733e213b1a2274d0b2ece40d2e174671180cb',
    200:'573eb8f58f098f1be1d5981372760e66461849553f132d14167d8d15fe0aa798',
    201:'9a5080f8b1cbdeb279283f81a2206a3f06f35f2798e866810a76a05836914b36',
    202:'a0561cc144fc95727be11f86070e09a5ae23039cccfe983e06e6d3e45574390e',
    203:'6ba83a2bb39e957e0d0fc95ba6d2a4692197040971adf4b8b6935f6627bc3f80',
    204:'1be5b8b977e1fc7db321d9a37f02a8ca3cb70e3326f266d1361efc75d1fb12db',
}
# Separately inspected speaker88 record; keep the older speaker24 profile exact.
# See docs/battle_unvoiced_source100_pending.json for original parser evidence.
UNVOICED_SOURCE_616='8dc76f3ef1ec61caaae5d35110fe96a49e94c895ac63fe065668efca223bb047'
# Separately inspected speaker124 source; keep the older admissions exact.
# See docs/battle_unvoiced_source106_pending.json for original parser evidence.
UNVOICED_SOURCE_720='a4b5032142d38ff2fbfabacc9a14d135312df5d056b1d925b6e90352eb9dc0ab'
# Source1439 has two calls, without the older profiles' trailing empty call.
# Admit its exact source only; see docs/battle_unvoiced_source131.json.
UNVOICED_SOURCE_1439='9cd701f1ca112e9c30f154436be7f5fa05a5509bc10bb131a7807b8e7aec801c'
PLAN=Path('work/translation/en/aliases.en.json')
sha=lambda data:hashlib.sha256(data).hexdigest()


def validate_table(raw,name):
    if name not in TABLES or sha(raw)!=SOURCE_SHA:
        raise ValueError('Unsupported battle-bank source revision')
    rows=parse_table(raw)
    if len(rows)!=SOURCE_ROWS:raise ValueError('Unexpected battle-bank row count')
    return rows


def original_tables(root=ROOT):
    result={}
    for name in TABLES:
        pn,mid=map(int,name.split('_'));pack=(root/f'work/source/afs/RESOURCE/{pn:05d}.bin').read_bytes()
        member=next(m for m in pack_members(pack) if m['id']==mid)
        raw=pack[member['offset']:member['offset']+member['size']]
        result[name]=validate_table(raw,name)
    if result[CANONICAL]!=result[ALIAS]:raise ValueError('Battle pair no longer identical')
    return result


def validate_row(source,english):
    if controls(source)!=controls(english):raise ValueError('Battle controls changed')
    old,new=pages(encode(source)),pages(encode(english))
    if len(old)!=len(new):raise ValueError('Battle native call count changed')
    bodies=voices=0
    for a,b in zip(old,new):
        meta=lambda p:{k:v for k,v in p.items() if k not in ('start','end','body')}
        if meta(a)!=meta(b):raise ValueError('Battle native staging changed')
        if a['flags']&~0x51 or a['function'] or a['arguments']:
            raise ValueError('Battle row needs another staging profile')
        bodies+=bool(a['flags']&1);voices+=bool(a['flags']&0x40)
    if bodies!=1:raise ValueError('Battle bark needs one original body')
    profile='voiced'
    if voices!=1:
        source_sha=sha(encode(source))
        if voices:raise ValueError('Unprofiled unvoiced battle source')
        flags=[0,0x11,0]
        if source_sha in UNVOICED_SOURCES.values():
            speaker,profile=24,'unvoiced-source-195-204'
        elif source_sha==UNVOICED_SOURCE_616:
            speaker,profile=88,'unvoiced-source-616'
        elif source_sha==UNVOICED_SOURCE_720:
            speaker,profile=124,'unvoiced-source-720'
        elif source_sha==UNVOICED_SOURCE_1439:
            speaker,profile,flags=280,'unvoiced-source-1439',[0,0x11]
        else:
            raise ValueError('Unprofiled unvoiced battle source')
        if [p['flags'] for p in old]!=flags or old[1]['speaker']!=speaker:
            raise ValueError('Unvoiced battle staging changed')
    # Only original speaker and voice headers, LF and NUL are admitted. Formatting,
    # runtime text, functions and escaped bytes need their own measured profile.
    for token in controls(english):
        if token=='{x00}':continue
        if not (token.upper().startswith('{C:8193') and len(token)==12 or
                token.upper().startswith('{C:81958296') and len(token)==24):
            raise ValueError('Unprofiled battle control')
    return profile


def expand_aliases(exports,plan,raw_tables):
    """Return only new target exports; fail on drift, overlap or missing sources."""
    if plan.get('schema')!='exact-source-aliases-v1':raise ValueError('Unknown alias schema')
    out={};seen=set()
    for item in plan['aliases']:
        src,dst=item['source_table'],item['target_table']
        if (src,dst)!=(CANONICAL,ALIAS) or item['whole_table_sha256']!=SOURCE_SHA:
            raise ValueError('Unapproved battle alias direction/revision')
        if dst in exports:raise ValueError('Alias conflicts with canonical target draft')
        if src not in exports:raise ValueError('Alias source export missing')
        source={r['id']:r for r in exports[src]['rows']}
        if len(source)!=len(exports[src]['rows']):raise ValueError('Duplicate canonical alias source')
        for mapping in item['rows']:
            i,j=mapping['source_id'],mapping['target_id']
            if type(i) is not int or type(j) is not int or i!=j or not 0<=i<len(raw_tables[src]) or not 0<=j<len(raw_tables[dst]):
                raise ValueError('Invalid explicit battle alias ID')
            if (dst,j) in seen:raise ValueError('Duplicate alias target')
            seen.add((dst,j))
            if i not in source:raise ValueError('Alias source row missing')
            raw=raw_tables[src][i]
            if raw!=raw_tables[dst][j] or sha(raw)!=mapping['source_sha256'] or source[i]['source_sha256']!=sha(raw):
                raise ValueError('Alias source bytes/hash differ')
            row=copy.deepcopy(source[i]);row['id']=j
            row['alias_of']=dict(table=src,id=i,source_sha256=sha(raw))
            row['review']['rendered_fit']='pending';row.pop('rendered_evidence',None)
            row['notes']='Exact original-source alias of '+src+':'+str(i)+'. Language review is shared; physical target display evidence remains pending.'
            evidence=mapping.get('rendered_evidence')
            if evidence and evidence.get('draft_sha256')==sha(row['en'].encode('utf-8')):
                required=('build','draft_sha256','built_row_sha256','native_sha256','pages','audit','build_elf_sha256')
                if any(k not in evidence for k in required) or not re.fullmatch(r'0\.\d+\.\d+',evidence['build']) or evidence['pages']<1:
                    raise ValueError('Incomplete physical alias fit evidence')
                row['review']['rendered_fit']='passed';row['rendered_evidence']={k:evidence[k] for k in required}
                row['notes']='Exact original-source alias of '+src+':'+str(i)+'. Language review is shared; this physical target has its own versioned native evidence.'
            out.setdefault(dst,dict(table=dst,rows=[]))['rows'].append(row)
    for value in out.values():value['rows'].sort(key=lambda r:r['id'])
    return out


def alias_exports(exports,root=ROOT):
    path=root/PLAN
    if not path.exists():return {}
    return expand_aliases(exports,json.loads(path.read_text(encoding='utf-8')),original_tables(root))


def validate_alias_exports(exports,root=ROOT):
    if ALIAS in exports and not (root/PLAN).exists():raise ValueError('Battle alias needs an explicit manifest')
    canonical={k:v for k,v in exports.items() if k!=ALIAS}
    for name,expected in alias_exports(canonical,root).items():
        if exports.get(name)!=expected:raise ValueError('Stale battle alias export; regenerate/check English exports')
