import argparse
import hashlib
import json
from pathlib import Path
from .firmware import verify_stock
from .frames import prepare_frames
from .packer import apply_runtime

def main() -> int:
    parser = argparse.ArgumentParser(description='Experimental n67cn 3.1.175 dynamic AOD, without writing firmware')
    commands = parser.add_subparsers(dest='command',required=True)
    check = commands.add_parser('check-firmware');check.add_argument('firmware',type=Path)
    pack = commands.add_parser('pack')
    pack.add_argument('--firmware',type=Path,required=True)
    pack.add_argument('--base-bin',type=Path,required=True)
    pack.add_argument('--frames',type=Path,required=True)
    pack.add_argument('--out',type=Path,required=True)
    pack.add_argument('--face-id',required=True)
    pack.add_argument('--title',default='Dynamic AOD Demo')
    pack.add_argument('--accept-experimental',action='store_true',help='Acknowledge firmware-specific native RAM execution')
    args = parser.parse_args()
    try:
        target = verify_stock(args.firmware)
        if args.command=='check-firmware':print(json.dumps(target,indent=2));return 0
        if not args.accept_experimental:raise ValueError('Read docs/METHOD.md, then explicitly pass --accept-experimental')
        if args.out.exists() or args.out.resolve()==args.base_bin.resolve():raise ValueError('Output must be a new file; originals are never overwritten')
        paths = sorted(args.frames.glob('*.png'))
        sequence = prepare_frames(paths)
        original = args.base_bin.read_bytes();pin = hashlib.sha256(original).hexdigest()
        result = apply_runtime(original,sequence,args.face_id,args.title)
        if hashlib.sha256(args.base_bin.read_bytes()).hexdigest()!=pin:raise ValueError('Base changed during build')
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open('xb') as out:out.write(result)
        print(json.dumps({'output':str(args.out),'bytes':len(result),'sha256':hashlib.sha256(result).hexdigest(),
                         'target':target,'frames':len(sequence.order),'unique_PNGs':len(sequence.files),
                         'target_interval_ms':40,'hardware_verified':False},indent=2))
        return 0
    except (ValueError,OSError) as error:
        parser.exit(2,f'Error: {error}\n')

if __name__=='__main__':raise SystemExit(main())
