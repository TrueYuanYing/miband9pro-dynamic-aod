"""Lossless visible-content crop and duplicate removal for monochrome AOD."""
import io
from dataclasses import dataclass
from pathlib import Path
from PIL import Image

@dataclass
class PreparedFrames:
    order: list[str]
    offsets: dict[str, tuple[int, int]]
    files: dict[str, bytes]
    pixels_before: int
    pixels_after: int

def prepare_frames(paths: list[Path]) -> PreparedFrames:
    if not 1 <= len(paths) <= 128:
        raise ValueError('Supply 1..128 frames; the hardware-tested sequence has 69')
    order, offsets, files, seen = [], {}, {}, {}
    before, after = 0, 0
    for index,path in enumerate(paths):
        with Image.open(path) as source:
            if source.size != (336,334):
                raise ValueError(f'{path.name}: expected 336x334 PNG canvas')
            image = source.convert('RGBA')
        rgba = bytearray(image.tobytes())
        for p in range(0,len(rgba),4):
            red,green,blue,alpha = rgba[p:p+4]
            if not alpha:
                rgba[p:p+4] = bytes(4)
            elif red != green or red != blue:
                raise ValueError(f'{path.name}: AOD must be monochrome')
        image = Image.frombytes('RGBA',image.size,bytes(rgba))
        bbox = image.getchannel('A').getbbox()
        if bbox:
            left,top,right,bottom = bbox
            box = (max(0,left-1),max(0,top-1),min(336,right+1),min(334,bottom+1))
        else:
            box = (0,0,1,1)
        cropped = image.crop(box)
        restored = Image.new('RGBA',image.size,(0,0,0,0));restored.paste(cropped,box[:2])
        if restored.tobytes() != image.tobytes():
            raise ValueError('Crop unexpectedly altered visible pixels')
        stream = io.BytesIO();cropped.save(stream,format='PNG',optimize=True)
        png = stream.getvalue();identity = (png,box[:2])
        before += 336*334
        if identity in seen:
            name = seen[identity]
        else:
            name = f'f{index:03d}.png';seen[identity] = name
            files[name] = png;offsets[name] = box[:2]
            after += cropped.width*cropped.height
        order.append(name)
    return PreparedFrames(order,offsets,files,before,after)
