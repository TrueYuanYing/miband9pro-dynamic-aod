"""Add the experiment to a compatible owner-supplied AOD watchface scaffold."""
import re
import struct
import hashlib
from .binfile import Watchface, lua_asset, read_asset
from .frames import PreparedFrames
from .runtime import RUNTIME, normal_script, aod_script

MODULE_SHA = 'fe8b72fb3faf1ba306a6caf9d74fe10e89d078c7349e20eec654110546e81c4e'
# Exact private reference loader, before the public error-path hardening.
REFERENCE_LOADER_SHA = 'a357474c911d911add7569a0f06498e5c2a051a902f2b9ad5519974b59258c5e'

def known_normal(content: bytes) -> bool:
    prefix = b'local LOADER_SOURCE=[=['
    if not content.startswith(prefix):return False
    loader, separator, suffix = content[len(prefix):].partition(b']=]\n')
    allowed = {REFERENCE_LOADER_SHA, hashlib.sha256((RUNTIME/'loader.lua').read_text(encoding='utf-8').encode()).hexdigest()}
    return bool(separator) and hashlib.sha256(loader).hexdigest() in allowed and suffix == (RUNTIME/'normal.lua').read_text(encoding='utf-8').encode()

def apply_runtime(blob: bytes, frames: PreparedFrames, face_id: str, title: str) -> bytes:
    face = Watchface(blob)
    if any(len(r)!=16 for _,r in face.sections[0x108]):
        raise ValueError('Malformed AOD layer; expected the known 16-byte layout')
    hosts = [struct.unpack('<IHHII',r) for _,r in face.sections[0x108] if struct.unpack_from('<I',r)[0]==0x050000DC]
    if len(hosts)!=1 or not (hosts[0][1]<336 and hosts[0][2]<480):
        raise ValueError('Base must already have the known visible AOD Lua host 0x050000dc')
    dark = []
    found = False
    for key,r in face.sections[0x130]:
        name,content = read_asset(r)
        if key == 0x050000DC:
            found = True;dark.append((key,lua_asset('_lua/aod16/play.lua',aod_script(frames))))
        elif re.fullmatch(r'_lua/aod16/f[0-9]{3}\.png',name):
            continue
        else:
            dark.append((key,r))
    if not found:raise ValueError('AOD Lua resource missing')
    used = {key for pair,rows in face.sections.items() if pair!=0x130 for key,_ in rows if key>>24}
    used.update(key for key,_ in dark if key>>24)
    for index,(name,png) in enumerate(frames.files.items()):
        key = 0x05020000+index
        if key in used:raise ValueError('New PNG resource ID collides with base')
        dark.append((key,lua_asset('_lua/aod16/'+name,png)))
    face.sections[0x130] = dark
    normal = face.sections[0xD8]
    if normal:
        content = read_asset(normal[0][1])[1] if len(normal)==1 else b''
        if not known_normal(content):
            raise ValueError('Unknown normal Lua code; integrate manually rather than overwrite it')
        key,_ = normal[0];face.sections[0xD8] = [(key,lua_asset('_lua/aod16/control_auto.lua',normal_script()))]
    else:
        key = 0x05010000
        if key in used:raise ValueError('Normal Lua resource ID collides with base')
        face.sections[0xD8] = [(key,lua_asset('_lua/aod16/control_auto.lua',normal_script()))]
        rows = face.sections[0xB0]
        actions = [r for r in rows if struct.unpack_from('<I',r[1])[0]>>24==9]
        layers = [r for r in rows if r not in actions]
        layers.append((0,struct.pack('<IHHII',key,0,0,0,0)))
        # Keep native weather/step/heart actions above the host's input surface.
        layers.extend(actions)
        face.sections[0xB0] = [(i,r) for i,(_,r) in enumerate(layers)]
    result = face.pack(face_id,title)
    Watchface(result)
    return result
