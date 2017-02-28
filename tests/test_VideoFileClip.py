import pytest
from moviepy.editor import *
import os

def test_setup():
    _red = ColorClip((1024,800), col=(255,0,0))
    _green = ColorClip((1024,800), col=(0,255,0))
    _blue = ColorClip((1024,800), col=(0,0,255))

    _red.fps=_green.fps=_blue.fps=30
    _video = clips_array([[_red, _green, _blue]]).set_duration(5)
    _video.write_videofile("/tmp/test.mp4")

    assert os.path.exists("/tmp/test.mp4")

    _clip = VideoFileClip("/tmp/test.mp4")
    assert _clip.duration == 5
    assert _clip.fps == 30
    assert _clip.size == [1024*3, 800]

if __name__ == '__main__':
   pytest.main()
