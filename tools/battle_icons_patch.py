"""Replace all eight Japanese unit-attribute icon cells; dry run by default."""
import argparse,json,struct,re
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from elf import ROOT
from extract import pack_members
from build import replace_pack,make_iso
import battle_ui_patch as prior
import fontgen

LANGUAGE=ROOT/'work/translation/en/battle-icons.en.json'
LANGUAGE_SHA='115fd57edd4b2181a242643537527567e6b5de97aab8a54c314fa414b9c25a35'
SOURCE_SHA='0ec38fa32a4a1575010a03a2d7384d5f63b9d9ca50fe15f13bc138dc12620f11'
digest=prior.digest
# Five-column pixel lettering keeps the two-character codes separated at native
# 16px size. Stretch vertically to9 rows without blurring the one-pixel stems.
SMALL={
 'A':['01110','10001','10001','11111','10001','10001','10001'],
 'T':['11111','00100','00100','00100','00100','00100','00100'],
 'D':['11110','10001','10001','10001','10001','10001','11110'],
 'F':['11111','10000','10000','11110','10000','10000','10000'],
 'L':['10000','10000','10000','10000','10000','10000','11111']}


def language():
    if digest(LANGUAGE.read_bytes())!=LANGUAGE_SHA:raise ValueError('Reviewed icon wording changed')
    obj=json.loads(LANGUAGE.read_text('utf-8'))
    if obj['review']!={'accuracy':'independent-reviewed','editorial':'complete','glossary':'complete','proofreading':'complete'}:
        raise ValueError('Icon language review incomplete')
    if [r['cell'] for r in obj['rows']] != [0,1,2,4,5,6,8,9]:
        raise ValueError('Icon inventory changed')
    return obj


def icon_member(blob):
    if digest(blob)!=SOURCE_SHA or len(blob)!=4432:
        raise ValueError('Unexpected unit-icon source or repeated patch')
    if struct.unpack_from('<HHI',blob,272)!=(20,64,64):
        raise ValueError('Unexpected icon texture layout')
    if digest(Path(fontgen.FONT_PATH).read_bytes())!='5113756f8a3b5d01b2211025e267c50121e3b36f465b7bbaf3cdaf4c3430bfd0':
        raise ValueError('Reviewed font revision changed')
    pal=[tuple(blob[128+4*i:132+4*i]) for i in range(16)]
    pixels=[v for q in blob[320:2368] for v in (q&15,q>>4)]
    if set(pixels)-set(range(6)):
        raise ValueError('Extra source palette indices would be affected')
    # Add ten neutral antialias shades in slots unused by every original cell.
    for i in range(6,16):pal[i]=(round((i-5)*255/11),)*3+(128,)
    out=bytearray(blob)
    for i in range(6,16):out[128+4*i:132+4*i]=bytes(pal[i])
    for row in language()['rows']:
        cell=row['cell'];ox=(cell%4)*16;oy=(cell//4)*16
        background=1 if cell<4 else 2 if cell<8 else 3
        # Retain the cell's transparent silhouette and source category colour.
        # Use a consistent black rim, clear sans glyph and one-pixel outline.
        mask=Image.new('L',(64,64));draw=ImageDraw.Draw(mask)
        font=fontgen._font((14 if len(row['en'])==1 else 10)*4,900)
        box=draw.textbbox((0,0),row['en'],font=font)
        w,h=box[2]-box[0],box[3]-box[1]
        if w>56 or h>48:raise ValueError('Icon abbreviation exceeds guarded glyph region')
        draw.text(((64-w)//2-box[0],(64-h)//2-box[1]),row['en'],font=font,fill=255)
        mask=mask.resize((16,16),Image.Resampling.LANCZOS)
        if len(row['en'])==2:
            pair=Image.new('L',(11,7))
            for j,ch in enumerate(row['en']):
                for y,line in enumerate(SMALL[ch]):
                    for x,value in enumerate(line):
                        if value=='1':pair.putpixel((j*6+x,y),255)
            mask=Image.new('L',(16,16));mask.paste(pair.resize((11,9),Image.Resampling.NEAREST),(2,3))
        hard=mask.point(lambda v:255 if v>=64 else 0)
        outline=hard.filter(ImageFilter.MaxFilter(3))
        ramp=[0]+list(range(6,16))+[5]
        for y in range(16):
            for x in range(16):
                pos=(oy+y)*64+ox+x
                if pixels[pos]==4:continue
                value=mask.getpixel((x,y))
                q=0 if x in (0,15) or y in (0,15) or outline.getpixel((x,y)) else background
                if value>=128:q=5
                elif value>=24:q=min(ramp,key=lambda i:abs(pal[i][0]-value))
                pixels[pos]=q
    out[320:2368]=fontgen.pack4(pixels)
    assert out[:152]==blob[:152] and out[192:320]==blob[192:320] and out[2368:]==blob[2368:]
    im=Image.frombytes('RGB',(64,64),bytes(c for p in pixels for c in pal[p][:3]))
    return bytes(out),im


def patch_pack(pack):
    m=next(m for m in pack_members(pack) if m['id']==10051)
    blob,im=icon_member(pack[m['offset']:m['offset']+m['size']])
    result=replace_pack(pack,{10051:blob})
    if len(result)!=len(pack):raise ValueError('Unexpected icon pack resize')
    return result,im


def inputs():
    data,packs,_,_=prior.inputs()
    packs[22],im=patch_pack(packs[22])
    return data,packs,dict(language_sha256=digest(LANGUAGE.read_bytes()),pack=22,member=10051,
        cells=language()['rows'],scope='Eight Japanese attribute/status cells; all other cells and CEL metadata retained.'),im


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');ap.add_argument('--preview',type=Path);a=ap.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+',a.version):raise ValueError('Expected0.x.y')
    data,packs,report,im=inputs()
    print(json.dumps(dict(version=a.version,elf_sha256=digest(data),**report),indent=1))
    if a.preview:im.resize((512,512),Image.Resampling.NEAREST).save(a.preview)
    if not a.write:print('DRY: no game data/ISO written.');return
    dest=ROOT/'work/output'/('v'+a.version)
    if dest.exists():raise FileExistsError(dest)
    dest.mkdir(parents=True);(dest/'SLPS_250.70').write_bytes(data)
    for n,p in packs.items():(dest/f'{n:05d}.pack').write_bytes(p)
    import menu_patch
    title=menu_patch.patch_title((ROOT/'work/source/afs/EVEMAP/00001.bin').read_bytes())
    image=dest/('Sunrise Eiyuutan 2 EN v'+a.version+'.iso');make_iso(image,data,packs,{1:title})
    info=json.loads((ROOT/'work/output/v0.2.3/build_info.json').read_text('utf8'))
    info.update(version=a.version,based_on='0.2.3',battle_icons=report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,in_game_validation='pending consolidated icon checks',scope='Eight unit attribute/status icons plus all retained0.2.3 content.')
    info.pop('native_validation_report',None)
    (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n',encoding='utf8')
    print('WRITE:',image)


if __name__=='__main__':main()
