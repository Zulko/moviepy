import pytest
from moviepy.editor import *

def test_clips_array():
    _red = ColorClip((1024,800), col=(255,0,0))
    _green = ColorClip((1024,800), col=(0,255,0))
    _blue = ColorClip((1024,800), col=(0,0,255))

    _video = clips_array([[_red, _green, _blue]])

    with pytest.raises(ValueError,
                       message="Expecting ValueError (duration not set)"):
       _video.resize(width=480).write_videofile("/tmp/test_clips_array.mp4")


def test_clips_array():
    _red = ColorClip((1024,800), col=(255,0,0))
    _green = ColorClip((1024,800), col=(0,255,0))
    _blue = ColorClip((1024,800), col=(0,0,255))

    _video = clips_array([[_red, _green, _blue]]).set_duration(5)

    with pytest.raises(AttributeError,
                       message="Expecting ValueError (fps not set)"):
         _video.write_videofile("/tmp/test_clips_array.mp4")


    #this one should work correctly
    _red.fps=_green.fps=_blue.fps=30
    _video = clips_array([[_red, _green, _blue]]).set_duration(5)
    _video.write_videofile("/tmp/test_clips_array.mp4")


if __name__ == '__main__':
   pytest.main()
