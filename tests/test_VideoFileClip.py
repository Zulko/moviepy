import pytest
from moviepy.editor import *
import os

def test_setup():
    red = ColorClip((1024,800), color=(255,0,0))
    green = ColorClip((1024,800), color=(0,255,0))
    blue = ColorClip((1024,800), color=(0,0,255))

    red.fps=green.fps=blue.fps=30
    video = clips_array([[red, green, blue]]).set_duration(5)
    video.write_videofile("/tmp/test.mp4")

    assert os.path.exists("/tmp/test.mp4")

    clip = VideoFileClip("/tmp/test.mp4")
    assert clip.duration == 5
    assert clip.fps == 30
    assert clip.size == [1024*3, 800]

if __name__ == '__main__':
   pytest.main()
