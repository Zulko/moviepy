import pytest
from moviepy.editor import *

import sys
sys.path.append("tests")
import download_media

def test_duration():
    clip = TextClip('hello world', size=(1280,720), color='white')
    clip.set_duration(5)
    assert clip.duration == 5

    clip2 = clip.fx(vfx.blink, d_on=1, d_off=1)
    clip2.set_duration(5)
    assert clip2.duration == 5

if __name__ == '__main__':
   pytest.main()
