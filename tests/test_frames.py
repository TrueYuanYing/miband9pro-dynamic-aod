import io
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from band9pro_aod.frames import prepare_frames

class FrameTests(unittest.TestCase):
    def test_crop_restores_black_composite_and_offsets(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'001.png';im=Image.new('RGBA',(336,334),(0,0,0,0))
            im.putpixel((70,80),(255,255,255,120));im.putpixel((90,110),(255,255,255,255));im.save(p)
            result=prepare_frames([p,p])
            self.assertEqual(result.order,['f000.png','f000.png'])
            self.assertEqual(len(result.files),1)
            x,y=result.offsets['f000.png'];cropped=Image.open(io.BytesIO(result.files['f000.png'])).convert('RGBA')
            restored=Image.new('RGBA',im.size);restored.paste(cropped,(x,y))
            self.assertEqual(restored.tobytes(),im.tobytes())
            self.assertLess(cropped.width*cropped.height,336*334/2)

    def test_rejects_color_and_mismatched_canvas(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a.png',Path(tmp)/'b.png'
            Image.new('RGBA',(336,334),(255,0,0,255)).save(a)
            with self.assertRaises(ValueError):prepare_frames([a])
            Image.new('RGBA',(100,100),(255,255,255,255)).save(b)
            with self.assertRaises(ValueError):prepare_frames([b])

    def test_handles_blank_and_rejects_empty_sequence(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'blank.png';Image.new('RGBA',(336,334),(255,255,255,0)).save(p)
            result=prepare_frames([p]);self.assertEqual(result.offsets['f000.png'],(0,0))
        with self.assertRaises(ValueError):prepare_frames([])

if __name__=='__main__':unittest.main()
