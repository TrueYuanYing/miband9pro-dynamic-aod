import struct
import unittest
from band9pro_aod.binfile import Watchface, lua_asset, read_asset, PAIRS

def sample():
    header=bytearray(0x158);header[:4]=bytes.fromhex('5aa53412')
    struct.pack_into('<I',header,0x10,0x800);struct.pack_into('<HH',header,0x1c,2,4)
    payload=lua_asset('_lua/aod16/play.lua',b'old player')
    struct.pack_into('<I',header,0x20,0x168);struct.pack_into('<I',header,0xac,0x168)
    for pair in PAIRS:struct.pack_into('<II',header,pair,0,0x158)
    struct.pack_into('<II',header,0x130,1,0x158)
    return bytes(header)+struct.pack('<4I',0x050000dc,0,0x16b,len(payload))+b'PNG'+payload

class BinTests(unittest.TestCase):
    def test_roundtrip_preserves_preview_and_unmodified_resources(self):
        face=Watchface(sample());result=Watchface(face.pack('123456789','Open AOD'))
        self.assertEqual(result.preview,b'PNG')
        self.assertEqual(result.sections,face.sections)
        self.assertEqual(result.header[0x68:0xa8].rstrip(b'\0'),b'Open AOD')

    def test_rejects_out_of_bounds_input(self):
        blob=bytearray(sample());struct.pack_into('<I',blob,0x158+8,0xfffffff0)
        with self.assertRaises(ValueError):Watchface(bytes(blob))

    def test_rejects_another_bin_layout(self):
        blob=bytearray(sample());struct.pack_into('<H',blob,0x1e,6)
        with self.assertRaises(ValueError):Watchface(bytes(blob))

    def test_resource_name_and_size_roundtrip(self):
        r=lua_asset('_lua/aod16/f000.png',b'abc')
        self.assertEqual(read_asset(r),('_lua/aod16/f000.png',b'abc'))

if __name__=='__main__':unittest.main()
