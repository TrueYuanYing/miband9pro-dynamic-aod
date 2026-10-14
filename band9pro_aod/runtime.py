"""Render the exact tested loader and cropped frame player into BIN resources."""
from pathlib import Path
from .frames import PreparedFrames

RUNTIME = Path(__file__).with_name('runtime')

def normal_script() -> bytes:
    loader = (RUNTIME/'loader.lua').read_text(encoding='utf-8')
    control = (RUNTIME/'normal.lua').read_text(encoding='utf-8')
    return ('local LOADER_SOURCE=[=['+loader+']=]\n'+control).encode()

def aod_script(frames: PreparedFrames) -> bytes:
    loader = (RUNTIME/'loader.lua').read_text(encoding='utf-8')
    player = (RUNTIME/'player.lua').read_text(encoding='utf-8')
    replacements = {
        '__FRAME_FILES__': '{'+','.join("'%s'"%name for name in frames.order)+'}',
        '__FRAME_OFFSETS__': '{'+','.join("['%s']={%d,%d}"%(name,*offset) for name,offset in frames.offsets.items())+'}',
        '__LAST_FRAME__': str(len(frames.order)-1),
    }
    for marker,value in replacements.items():
        if player.count(marker) != 1:raise ValueError('Invalid runtime template')
        player = player.replace(marker,value)
    return ('local LOADER_SOURCE=[=['+loader+']=]\n'+player).encode()
