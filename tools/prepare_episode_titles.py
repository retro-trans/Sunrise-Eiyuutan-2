"""Freeze all nineteen reviewed save/load title-table translations."""
import argparse,json,struct,hashlib
from elf import ROOT,PATH,Elf
sha=lambda b:hashlib.sha256(b).hexdigest()
DEST=ROOT/'work/translation/en/episode-titles.en.json'
def collect():
 source=Elf(PATH.read_bytes());current=Elf((ROOT/'work/output/v0.2.26/SLPS_250.70').read_bytes())
 files=[ROOT/'work/source/episode_titles_audit_027.json',ROOT/'work/translation/en/pending/compiled_rodata_indices80_159_language540.json']
 audit=json.loads(files[0].read_text('utf8'));existing=json.loads(files[1].read_text('utf8'))
 reviewed={r['va']:r for r in existing['rows'] if r.get('review',{}).get('accuracy')=='independent-reviewed'}
 reviewed.update({r['va']:r for r in audit['rows']});rows=[];prefixes=[]
 for i in range(19):
  site=0x221f68+i*4;va=struct.unpack('<I',source.at(site,4))[0];raw=source.at(va,256).split(b'\0')[0];r=reviewed[va]
  if sha(raw)!=r['source_sha256']:raise ValueError('Reviewed source changed')
  r['en'].encode('cp932')
  rows.append(dict(index=i,va=va,site=site,expected_pointer=struct.unpack('<I',current.at(site,4))[0],source_size=len(raw)+1,source_sha256=sha(raw),source_with_nul_sha256=sha(raw+b'\0'),en=r['en'],review=r['review']))
  ps=0x221de8+i*4;ptr=struct.unpack('<I',current.at(ps,4))[0];praw=current.at(ptr,256).split(b'\0')[0]
  prefixes.append(dict(index=i,site=ps,pointer=ptr,en=praw.decode('cp932'),raw_hex=praw.hex()))
 lengths=[len(p['en'].encode('cp932')+r['en'].encode('cp932')) for p in prefixes for r in rows]
 if max(lengths)>63:raise ValueError('A complete combination exceeds caller 64-byte slot')
 return dict(version='0.2.27',source_elf_sha256=sha(source.data),inputs={str(f.relative_to(ROOT)):sha(f.read_bytes())for f in files},review_scope='All 19 source titles and prefixes examined; 16 existing independent reviews, three new separate accuracy/editorial/proofreading reviews. Prefix/title indices independent.',maximum_combined_bytes=max(lengths),prefixes=prefixes,rows=rows)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();d=collect();print(json.dumps(dict(count=len(d['rows']),maximum_combined_bytes=d['maximum_combined_bytes'],titles=[r['en']for r in d['rows']]),indent=1),flush=True)
 if not a.write:print('DRY no language file written.');return
 if DEST.exists():raise FileExistsError(DEST)
 DEST.write_text(json.dumps(d,indent=1)+'\n','utf8');print('WRITE',DEST,'SHA',sha(DEST.read_bytes()))
if __name__=='__main__':main()
