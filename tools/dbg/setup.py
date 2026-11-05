"""Prepare an isolated, muted portable emulator from the existing sibling installation."""
import argparse
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT.parent/'Sunrise Eiyuutan/work/emulator/pcsx2'
DEST=ROOT/'work/emulator/pcsx2'


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    files=[p for p in SOURCE.iterdir() if p.is_file() and (p.suffix.lower() in ('.exe','.dll') or p.name in ('qt.conf','portable.txt'))]
    dirs=['QtPlugins','resources','bios','D3D12']
    print('Source:',SOURCE,'Destination:',DEST)
    print('Runtime files:',len(files),'directories:',dirs)
    print('Fresh settings: PINE 28026, audio muted, memory cards disabled, no imported saves')
    if not args.write:
        print('DRY RUN: --write copies runtime and BIOS; existing destination settings are refused');return
    if (DEST/'inis/PCSX2.ini').exists():raise FileExistsError('Destination already configured')
    DEST.mkdir(parents=True,exist_ok=True)
    for p in files:shutil.copy2(p,DEST/p.name)
    for d in dirs:shutil.copytree(SOURCE/d,DEST/d,dirs_exist_ok=True)
    config='''[UI]
SetupWizardIncomplete = false
ConfirmShutdown = false
SettingsVersion = 1
PauseOnFocusLoss = false
StartFullscreen = false

[Folders]
Bios = bios
Snapshots = snaps
Savestates = sstates
MemoryCards = memcards
Logs = logs
Cache = cache

[Filenames]
BIOS = scph39001.bin

[EmuCore]
EnableFastBoot = true
EnablePINE = true
PINESlot = 28026
EnableCheats = false
EnablePatches = false
SaveStateOnShutdown = false
BackupSavestate = false

[MemoryCards]
Slot1_Enable = false
Slot2_Enable = false

[AutoUpdater]
CheckAtStartup = false

[SPU2/Output]
OutputMuted = true
StandardVolume = 0

[Pad1]
Type = DualShock2

[EmuCore/GS]
upscale_multiplier = 1
VsyncEnable = false
'''
    (DEST/'inis').mkdir(exist_ok=True)
    (DEST/'inis/PCSX2.ini').write_text(config,encoding='utf-8')


if __name__=='__main__':main()
