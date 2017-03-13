import pytest
from moviepy.editor import *

def test_clips_array():
    red = ColorClip((1024,800), color=(255,0,0))
    green = ColorClip((1024,800), color=(0,255,0))
    blue = ColorClip((1024,800), color=(0,0,255))

    video = clips_array([[red, green, blue]])

    with pytest.raises(ValueError,
                       message="Expecting ValueError (duration not set)"):
       video.resize(width=480).write_videofile("/tmp/test_clips_array.mp4")


def test_clips_array():
    red = ColorClip((1024,800), color=(255,0,0))
    green = ColorClip((1024,800), color=(0,255,0))
    blue = ColorClip((1024,800), color=(0,0,255))

    video = clips_array([[red, green, blue]]).set_duration(5)

    with pytest.raises(AttributeError,
                       message="Expecting ValueError (fps not set)"):
         video.write_videofile("/tmp/test_clips_array.mp4")


    #this one should work correctly
    red.fps=green.fps=blue.fps=30
    video = clips_array([[red, green, blue]]).set_duration(5)
    video.write_videofile("/tmp/test_clips_array.mp4")


if __name__ == '__main__':
   pytest.main()
