"""Read the owner's stock file for target checking; never write its contents."""
import hashlib
import io
import re
import struct
import zipfile
from pathlib import Path

STOCK_SHA256 = 'a8274e4cb29c427e020d08b7be109478750fb883498fd4bab0aad2064ef7131c'
AP_SHA256 = '4f43b325addd6d9e6e7c7e2a4d00ffe3f23d5fb1560d8fe503544002ac1f516b'

def verify_stock(path: Path) -> dict:
    blob = path.read_bytes()
    if hashlib.sha256(blob).hexdigest() != STOCK_SHA256:
        raise ValueError('This tool is pinned to the exact stock CN 3.1.175 file')
    for match in re.finditer(re.escape(b'PK\x05\x06'),blob):
        end = match.start()
        if end+22 > len(blob):continue
        disk,other,count,count2,size,offset,comment = struct.unpack_from('<4H2IH',blob,end+4)
        start = end-size-offset
        if disk or other or count != count2 or start < 0 or blob[start:start+4] != b'PK\x03\x04':continue
        with zipfile.ZipFile(io.BytesIO(blob[start:end+22+comment])) as archive:
            if 'vela_ap.bin' not in archive.namelist():continue
            ap = archive.read('vela_ap.bin')
        if hashlib.sha256(ap).hexdigest() != AP_SHA256:
            raise ValueError('AP image does not match the supported target')
        return {'model':'n67cn','firmware':'3.1.175','stock_sha256':STOCK_SHA256,'ap_sha256':AP_SHA256}
    raise ValueError('Stock AP image was not found')
