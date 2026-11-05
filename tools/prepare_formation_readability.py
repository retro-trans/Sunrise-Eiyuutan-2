"""Freeze reviewed class, captain-name and submenu text with native field guards."""
import argparse,json,hashlib
from elf import ROOT,PATH,Elf
DEST=ROOT/'work/translation/en/formation-readability.en.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
AUDIT=ROOT/'work/source/formation_text_audit_029.json'
AUDIT_SHA='56b33bcfb60263262ca610b443706d0884abe1e1534ba0da8abdc841976843b3'
def collect():
 raw=AUDIT.read_bytes();audit=json.loads(raw)
 if sha(raw)!=AUDIT_SHA or audit['unresolved_entries']:raise ValueError('Independent audit incomplete or changed')
 e=Elf((ROOT/'work/output/v0.2.28/SLPS_250.70').read_bytes());source=Elf(PATH.read_bytes());rows=[];protected=[]
 for r in audit['rows']:
  old=source.at(r['va'],512).split(b'\0')[0]+b'\0'
  if sha(old)!=r['source_with_nul_sha256']:raise ValueError('Source changed')
  refs=[]
  for use in r['uses']:
   if use.get('pilot')==1:protected.append(dict(**use,pointer=int.from_bytes(e.at(use['site'],4),'little')));continue
   site=use['site'];refs.append(dict(**use,expected=int.from_bytes(e.at(site,4),'little')))
  rows.append(dict(va=r['va'],category=r['category'],source_size=len(old),source_with_nul_sha256=sha(old),en=r['en'],refs=refs,review=r['review'],origin=r['origin'],rationale=r['rationale']))
 return dict(version='0.2.29',baseline_elf_sha256=sha(e.data),source_elf_sha256=sha(source.data),audit_sha256=AUDIT_SHA,review_order=audit['review_order'],qualifications=audit['qualifications'],rows_examined=audit['rows_examined'],protected_player=protected,rows=rows)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();d=collect();print(json.dumps(dict(objects=len(d['rows']),refs=sum(len(r['refs'])for r in d['rows']),protected_player=d['protected_player'],sample=[dict(va=hex(r['va']),en=r['en'],refs=r['refs'])for r in d['rows']if r['va']in(0x22b638,0x22ad20,0x238c88,0x238c90)]),indent=1),flush=True)
 if not a.write:print('DRY no reviewed snapshot written.');return
 if DEST.exists():raise FileExistsError(DEST)
 DEST.write_text(json.dumps(d,indent=1)+'\n','utf8');print('WRITE',DEST,'SHA',sha(DEST.read_bytes()))
if __name__=='__main__':main()
