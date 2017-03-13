import pytest
from moviepy.editor import *
import moviepy.video.tools.cuts as cuts

import sys
sys.path.append("tests")
import download_media

def test_download_media(capsys):
    with capsys.disabled():
       download_media.download()

def test_cuts1():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").resize(0.2)
    cuts.find_video_period(clip) == pytest.approx(0.966666666667, 0.0001)


if __name__ == '__main__':
   pytest.main()
