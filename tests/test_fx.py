import pytest
from moviepy.editor import *

from moviepy.video.fx.crop import crop

import os
import sys
sys.path.append("tests")
import download_media
from test_helper import TRAVIS, TMP_DIR


def test_download_media(capsys):
    with capsys.disabled():
       download_media.download()

def test_crop():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm")

    clip1=crop(clip)   #ie, no cropping (just tests all default values)
    clip1.write_videofile(os.path.join(TMP_DIR, "clip1.webm"))

    clip2=crop(clip, x1=50, y1=60, x2=460, y2=275)
    clip2.write_videofile(os.path.join(TMP_DIR, "clip2.webm"))

    clip3=crop(clip, y1=30)  #remove part above y=30
    clip3.write_videofile(os.path.join(TMP_DIR, "clip3.webm"))

    clip4=crop(clip, x1=10, width=200) # crop a rect that has width=200
    clip4.write_videofile(os.path.join(TMP_DIR, "clip4.webm"))

    clip5=crop(clip, x_center=300, y_center=400, width=50, height=150)
    clip5.write_videofile(os.path.join(TMP_DIR, "clip5.webm"))

    clip6=crop(clip, x_center=300, width=400, y1=100, y2=600)
    clip6.write_videofile(os.path.join(TMP_DIR, "clip6.webm"))

if __name__ == '__main__':
   pytest.main()
