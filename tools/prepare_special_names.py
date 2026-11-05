"""Freeze reviewed special-attack full/display/omission names."""
import argparse,json,hashlib,struct
from elf import ROOT,PATH,Elf
sha=lambda b:hashlib.sha256(b).hexdigest()
DEST=ROOT/'work/translation/en/special-names.en.json'

def collect():
 e=Elf(PATH.read_bytes());auditfile=ROOT/'work/source/special_names_audit_026.json';audit=json.loads(auditfile.read_text('utf8'));extra={r['va']:r for r in audit['rows']};catalog={}
 for f in(ROOT/'work/source/candidates/ELF').glob('*.json'):
  catalog.update({r.get('va'):r for r in json.loads(f.read_text('utf8')).get('rows',[])})
 pf=ROOT/'work/translation/en/compiled-proposals.en.json';pro={r['id']:r for r in json.loads(pf.read_text('utf8'))['rows']};refs={};rows=[];inputs={str(pf.relative_to(ROOT)):sha(pf.read_bytes()),str(auditfile.relative_to(ROOT)):sha(auditfile.read_bytes())}
 for i in range(118):
  for f in(4,8,12):
   site=0x1fd5e8+i*60+f;va=struct.unpack('<I',e.at(site,4))[0];refs.setdefault(va,[]).append(dict(row=i,field=f,site=site))
 for va,fields in refs.items():
  raw=e.at(va,512).split(b'\0')[0];c=catalog.get(va,dict(id=f'ELF/va:{va:08X}'));r=extra.get(va);normalization=None
  if r:
   if r['source_sha256']!=sha(raw):raise ValueError('Independent source guard changed')
   en=r['en'];evidence='Independent 026 source accuracy, editorial and proofreading audit.'
  else:
   p=pro[c['id']]
   if p['status']!='language-ready'or p['source_sha256']!=sha(raw):raise ValueError('Existing source review absent')
   en=p['en'];evidence='Existing complete compiled accuracy/editorial/proof review.'
   for name in p['artifacts']:
    f=ROOT/name;inputs[name]=sha(f.read_bytes());record=next(x for x in json.loads(f.read_text('utf8'))['rows']if x['id']==c['id'])
    if record['en']!=en or record['review']['accuracy']!='independent-reviewed':raise ValueError('Completed reviewed English changed')
  if 'Ｖ－ＭＡＸ'in en:en=en.replace('Ｖ－ＭＡＸ','V-MAX');normalization='Registered V-MAX ASCII typography applied after language review.'
  en.encode('ascii');omit='Omni. Mega-Particle Cannon'if va==0x232268 else en
  rows.append(dict(id=c['id'],va=va,source_size=len(raw)+1,source_sha256=sha(raw),source_with_nul_sha256=sha(raw+b'\0'),en=en,omit_en=omit,refs=fields,review=evidence,normalization=normalization))
 if len(rows)!=50 or sum(len(r['refs'])for r in rows)!=354:raise ValueError('Complete special-name inventory changed')
 return dict(version='0.2.26',source_elf_sha256=sha(e.data),table=dict(va=0x1fd5e8,records=118,stride=60,fields=[4,8,12]),review=dict(accuracy='existing-independent-plus-026-audit',editorial='existing-plus-026-complete-read',glossary='registered-spellings-and-V-MAX-typography',proofreading='existing-plus-026-complete-read'),abbreviation=dict(field='omit only',source_va=0x232268,full='Omnidirectional Mega-Particle Cannon',short='Omni. Mega-Particle Cannon',meaning='Omni. expands to Omnidirectional; complete full/display name retained.'),inputs=inputs,rows=rows)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();d=collect();print(json.dumps(dict(distinct_names=len(d['rows']),fields=354,samples=[r for r in d['rows']if r['va']in(0x232360,0x232268,0x2390a8,0x2390a0)],abbreviation=d['abbreviation']),indent=1),flush=True)
 if not a.write:print('DRY no language snapshot written.');return
 if DEST.exists():raise FileExistsError(DEST)
 DEST.write_text(json.dumps(d,indent=1)+'\n','utf8');print('WRITE',DEST,'SHA',sha(DEST.read_bytes()))
if __name__=='__main__':main()
