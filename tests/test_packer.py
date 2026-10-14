import hashlib
import struct
import unittest
from band9pro_aod.binfile import Watchface, lua_asset, read_asset
from band9pro_aod.frames import PreparedFrames
from band9pro_aod.packer import apply_runtime, MODULE_SHA
from test_package import sample
from band9pro_aod.runtime import normal_script

def scaffold():
    face=Watchface(sample())
    face.sections[0x108]=[(0,struct.pack('<IHHII',0x050000dc,0,12,0,0))]
    return face.pack('123456789','Base')

class PackerTests(unittest.TestCase):
    def frames(self):return PreparedFrames(['f000.png'],{'f000.png':(1,2)},{'f000.png':b'png'},1,1)

    def test_adds_runtime_without_changing_base_preview_or_calendar(self):
        original=scaffold();pin=hashlib.sha256(original).digest()
        out=Watchface(apply_runtime(original,self.frames(),'987654321','Open AOD'))
        before=Watchface(original)
        self.assertEqual(hashlib.sha256(original).digest(),pin)
        self.assertEqual(out.preview,before.preview)
        self.assertEqual(out.sections[0x140],before.sections[0x140])
        self.assertEqual(out.sections[0x108],before.sections[0x108])
        self.assertEqual(len(out.sections[0xd8]),1)
        self.assertIn(b'local last = 0',read_asset(out.sections[0x130][0][1])[1])

    def test_missing_host_or_foreign_normal_lua_is_rejected(self):
        with self.assertRaises(ValueError):apply_runtime(sample(),self.frames(),'987654321','Open AOD')
        face=Watchface(scaffold())
        face.sections[0xd8]=[(0x05010000,lua_asset('other.lua',(MODULE_SHA+'\ncustom behavior').encode()))]
        with self.assertRaises(ValueError):apply_runtime(face.pack('123456789','Base'),self.frames(),'987654321','Open AOD')

    def test_unknown_code_inside_loader_is_rejected(self):
        face=Watchface(scaffold())
        code=normal_script().replace(b'local MODULE_SHA',b"os.execute('unknown');local MODULE_SHA",1)
        face.sections[0xd8]=[(0x05010000,lua_asset('control.lua',code))]
        with self.assertRaises(ValueError):apply_runtime(face.pack('123456789','Base'),self.frames(),'987654321','Open AOD')

    def test_foreign_frames_survive_and_own_output_can_be_repacked(self):
        face=Watchface(scaffold())
        extra=(0x050000df,lua_asset('_lua/calendar/f001.png',b'foreign pixels'))
        face.sections[0x130].append(extra)
        out=apply_runtime(face.pack('123456789','Base'),self.frames(),'987654321','Open AOD')
        again=Watchface(apply_runtime(out,self.frames(),'987654320','Next AOD'))
        self.assertIn(extra,again.sections[0x130])
        self.assertEqual(len([k for k,r in again.sections[0x130] if k==0x05020000]),1)

    def test_non_ascii_face_id_is_rejected(self):
        with self.assertRaises(ValueError):Watchface(scaffold()).pack('１２３４５６７８９','Base')

    def test_truncated_or_off_screen_host_is_rejected(self):
        for layer in (struct.pack('<I',0x050000dc),struct.pack('<IHHII',0x050000dc,336,0,0,0)):
            face=Watchface(scaffold());face.sections[0x108]=[(0,layer)]
            with self.assertRaises(ValueError):apply_runtime(face.pack('123456789','Base'),self.frames(),'987654321','Open AOD')

if __name__=='__main__':unittest.main()
