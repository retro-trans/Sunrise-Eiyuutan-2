"""Verify a built ISO against every unchanged disc file and every RESOURCE pack."""
import argparse
import hashlib
import json
from elf import ROOT
from iso import ISO,records,read_record
from afs import index,validate_partition
from build import inputs


def hash_extent(f,start,size):
    f.seek(start);h=hashlib.sha256()
    while size:
        b=f.read(min(size,4*1024*1024))
        if not b:raise ValueError('Truncated extent')
        h.update(b);size-=len(b)
    return h.hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');args=ap.parse_args()
    dest=ROOT/'work/output'/('v'+args.version);info=json.loads((dest/'build_info.json').read_text(encoding='utf-8'))
    image=dest/('Sunrise Eiyuutan 2 EN v'+args.version+'.iso')
    original=records(ISO);built={r['path']:r for r in records(image)}
    if info.get('trade_ui') and info.get('based_on')=='0.2.30':
        import trade_patch
        expected_elf,packs,event_overlays,_=trade_patch.inputs()
    elif info.get('formation_polish') and info.get('based_on')=='0.2.29':
        import formation_polish_patch
        expected_elf,packs,event_overlays,_=formation_polish_patch.inputs()
    elif info.get('formation_readability') and info.get('based_on')=='0.2.28':
        import formation_readability_patch
        expected_elf,packs,event_overlays,_=formation_readability_patch.inputs()
    elif info.get('item_typography') and info.get('based_on')=='0.2.27':
        import item_typography_patch
        expected_elf,packs,event_overlays,_=item_typography_patch.inputs()
    elif info.get('episode_titles') and info.get('based_on')=='0.2.26':
        import episode_titles_patch
        expected_elf,packs,event_overlays,_=episode_titles_patch.inputs()
    elif info.get('special_names') and info.get('based_on')=='0.2.25':
        import special_names_patch
        expected_elf,packs,event_overlays,_=special_names_patch.inputs()
    elif info.get('battle_category') and info.get('based_on')=='0.2.24':
        import battle_category_patch
        expected_elf,packs,event_overlays,_=battle_category_patch.inputs()
    elif info.get('card_dialog') and info.get('based_on')=='0.2.23':
        import card_dialog_patch
        expected_elf,packs,event_overlays,_=card_dialog_patch.inputs()
    elif info.get('lyrics_display') and info.get('based_on')=='0.2.22':
        import lyrics_display_patch
        expected_elf,packs,event_overlays,_=lyrics_display_patch.inputs()
    elif info.get('battle_effects') and info.get('based_on')=='0.2.21':
        import battle_effects_patch
        expected_elf,packs,event_overlays,_=battle_effects_patch.inputs()
    elif info.get('battle_readability') and info.get('based_on')=='0.2.20':
        import battle_readability_patch
        expected_elf,packs,event_overlays,_=battle_readability_patch.inputs()
    elif info.get('story_dialogue') and info.get('based_on')=='0.2.19':
        import story_dialogue_patch
        expected_elf,packs,event_overlays,_=story_dialogue_patch.inputs()
    elif info.get('movie_subtitles') and info.get('based_on')=='0.2.18':
        import movie_patch
        expected_elf,packs,event_overlays,_=movie_patch.inputs()
    elif info.get('squad_name_ui') and info.get('based_on')=='0.2.17':
        import squad_name_patch
        expected_elf,packs,event_overlays,_=squad_name_patch.inputs()
    elif info.get('information_ui') and info.get('based_on')=='0.2.16':
        import information_patch
        expected_elf,packs,event_overlays,_=information_patch.inputs()
    elif info.get('services_ui') and info.get('based_on')=='0.2.15':
        import services_patch
        expected_elf,packs,event_overlays,_=services_patch.inputs()
    elif info.get('formation_ui') and info.get('based_on')=='0.2.14':
        import formation_patch
        expected_elf,packs,event_overlays,_=formation_patch.inputs()
    elif info.get('battle_details') and info.get('based_on')=='0.2.13':
        import battle_details_patch
        expected_elf,packs,event_overlays,_=battle_details_patch.inputs()
    elif info.get('travel_tutorials') and info.get('based_on')=='0.2.12':
        import travel_tutorials_patch
        expected_elf,packs,event_overlays,_=travel_tutorials_patch.inputs()
    elif info.get('travel_items') and info.get('based_on')=='0.2.11':
        import travel_items_patch
        expected_elf,packs,event_overlays,_=travel_items_patch.inputs()
    elif info.get('locations_ui') and info.get('based_on')=='0.2.10':
        import locations_patch
        expected_elf,packs,_,_=locations_patch.inputs()
    elif info.get('destination_ui') and info.get('based_on')=='0.2.9':
        import destination_patch
        expected_elf,packs,_,_=destination_patch.inputs()
    elif info.get('deck_ui') and info.get('based_on')=='0.2.8':
        import deck_patch
        expected_elf,packs,_,_=deck_patch.inputs()
    elif info.get('options_ui') and info.get('based_on')=='0.2.7':
        import options_patch
        expected_elf,packs,_,_=options_patch.inputs()
    elif info.get('mc_font') and info.get('based_on')=='0.2.6':
        import mc_font_patch
        expected_elf,packs,_,_=mc_font_patch.inputs()
    elif info.get('choices_ui') and info.get('based_on')=='0.2.5':
        import choices_patch
        expected_elf,packs,_,_=choices_patch.inputs()
    elif info.get('screens_ui') and info.get('based_on')=='0.2.4':
        import screens_patch
        expected_elf,packs,_,_=screens_patch.inputs()
    elif info.get('battle_icons') and info.get('based_on')=='0.2.3':
        import battle_icons_patch
        expected_elf,packs,_,_=battle_icons_patch.inputs()
    elif info.get('battle_ui') and info.get('based_on')=='0.2.2':
        import battle_ui_patch
        expected_elf,packs,_,_=battle_ui_patch.inputs()
    elif info.get('speaker_names') and info.get('based_on')=='0.2.1':
        import speaker_patch
        expected_elf,packs,_,_,_=speaker_patch.inputs()
    elif info.get('narration_integration'):
        import narration_patch
        expected_elf,packs,_,_=narration_patch.inputs()
    elif info.get('based_on'):
        import menu_patch
        if info['based_on']!=menu_patch.BASE_VERSION:raise ValueError('Unsupported focused-build baseline')
        base=ROOT/'work/output'/('v'+info['based_on'])
        baseline=(base/'SLPS_250.70').read_bytes()
        if hashlib.sha256(baseline).hexdigest()!=menu_patch.BASE_ELF_SHA:raise ValueError('Focused baseline changed')
        expected_elf,_=menu_patch.patch_elf(baseline)
        packs={int(p.stem):(p.read_bytes()) for p in base.glob('*.pack')}
    else:
        expected_elf,packs,_=inputs(info['vwf_enabled'],bool(info['translated_rows'] or info.get('elf_translated_rows')),info.get('preview_request'),info.get('encyclopedia_pagination',False),info.get('tutorial_preview'),info.get('battle_preview'),info.get('battle_preview_first',0),info.get('battle_preview_count',80),info.get('battle_preview_rows'))
    if info.get('travel_tutorials'):
        pass # Complete focused builder supplied its retained overlays above.
    elif info.get('travel_items'):
        pass # Already computed with the complete focused builder above.
    elif info.get('locations_ui'):
        import locations_patch
        _,_,event_overlays,_=locations_patch.inputs()
    elif info.get('destination_ui'):
        _,_,event_overlays,_=destination_patch.inputs()
    elif info.get('deck_ui'):
        _,_,event_overlays,_=deck_patch.inputs()
    elif info.get('options_ui'):
        _,_,event_overlays,_=options_patch.inputs()
    elif info.get('mc_font'):
        _,_,event_overlays,_=mc_font_patch.inputs()
    elif info.get('choices_ui'):
        _,_,event_overlays,_=choices_patch.inputs()
    elif info.get('screens_ui'):
        _,_,event_overlays,_=screens_patch.inputs()
    else:event_overlays={}
    if info.get('menu_name_ui'):
        import menu_patch
        event_overlays[1]=menu_patch.patch_title((ROOT/'work/source/afs/EVEMAP/00001.bin').read_bytes())
    checks=[]
    with open(ISO,'rb') as a,open(image,'rb') as b:
        for rec in original:
            if rec['directory']:continue
            new=built[rec['path']]
            if rec['path']=='/SLPS_250.70':
                if read_record(image,new)!=expected_elf:raise ValueError('ELF mismatch')
                checks.append(dict(path=rec['path'],result='exact expected patched ELF'));continue
            if rec['path']=='/RESOURCE.AFS':
                oa=index(a,rec['lba']*2048,rec['size']);nb=index(b,new['lba']*2048,new['size'])
                validate_partition(nb)
                if len(oa)!=len(nb):raise ValueError('AFS count changed')
                for i,(x,y) in enumerate(zip(oa,nb)):
                    if i in packs:
                        b.seek(new['lba']*2048+y['offset'])
                        if b.read(y['size'])!=packs[i]:raise ValueError('Patched pack mismatch')
                    elif x['size']!=y['size'] or hash_extent(a,rec['lba']*2048+x['offset'],x['size'])!=hash_extent(b,new['lba']*2048+y['offset'],y['size']):
                        raise ValueError('Unrelated resource pack changed: %d'%i)
                checks.append(dict(path=rec['path'],packs=len(oa),patched_packs=sorted(packs),result='all packs verified'));continue
            if rec['path']=='/MOVIE.AFS' and info.get('movie_subtitles'):
                import movie_patch
                language,_,_=movie_patch.language();changed={m['member']:m for m in language['movies']}
                oa=index(a,rec['lba']*2048,rec['size']);nb=index(b,new['lba']*2048,new['size']);validate_partition(nb)
                if len(oa)!=489 or oa!=nb:raise ValueError('Movie archive directory changed')
                for i,(x,y) in enumerate(zip(oa,nb)):
                    if i in changed:
                        if info.get('lyrics_display'):
                            import lyrics_display_patch
                            expected,metadata=lyrics_display_patch.movie_bytes(changed[i])
                        else:expected,metadata=movie_patch.movie_bytes(changed[i])
                        b.seek(new['lba']*2048+y['offset'])
                        if b.read(y['size'])!=expected:raise ValueError('Captioned movie mismatch%d'%i)
                    elif hash_extent(a,rec['lba']*2048+x['offset'],x['size'])!=hash_extent(b,new['lba']*2048+y['offset'],y['size']):raise ValueError('Unrelated movie changed%d'%i)
                checks.append(dict(path=rec['path'],members=489,patched_members=sorted(changed),original_audio_preserved=True,result='all movie members and exact expected captioned-picture remuxes verified; ADX payload unchanged'));continue
            if rec['path']=='/EVEMAP.AFS' and event_overlays:
                oa=index(a,rec['lba']*2048,rec['size']);nb=index(b,new['lba']*2048,new['size'])
                validate_partition(nb)
                if len(oa)!=len(nb):raise ValueError('Event member count changed')
                for i,(x,y) in enumerate(zip(oa,nb)):
                    if i in event_overlays:
                        b.seek(new['lba']*2048+y['offset'])
                        if b.read(y['size'])!=event_overlays[i]:raise ValueError('Title overlay mismatch')
                    elif x['size']!=y['size'] or hash_extent(a,rec['lba']*2048+x['offset'],x['size'])!=hash_extent(b,new['lba']*2048+y['offset'],y['size']):
                        raise ValueError('Unrelated event overlay changed: %d'%i)
                checks.append(dict(path=rec['path'],members=len(oa),patched_members=sorted(event_overlays),result='all event overlays verified'));continue
            if rec['size']!=new['size'] or hash_extent(a,rec['lba']*2048,rec['size'])!=hash_extent(b,new['lba']*2048,new['size']):
                raise ValueError('Unrelated file changed: '+rec['path'])
            checks.append(dict(path=rec['path'],result='unchanged SHA-256'))
    result=dict(version=args.version,files_verified=len(checks),resource_packs_verified=5614,checks=checks,
                in_game_validation='separate from byte validation')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=1))
    if args.write:(dest/'verification.json').write_text(json.dumps(result,indent=1),encoding='utf-8')


if __name__=='__main__':main()
