# -*- coding: utf-8 -*-
"""Compositing tests for use with pytest."""
from os.path import join
import sys
import pytest
from moviepy.editor import *
sys.path.append("tests")
from test_helper import TMP_DIR

def test_clips_array():
    red = ColorClip((1024,800), color=(255,0,0))
    green = ColorClip((1024,800), color=(0,255,0))
    blue = ColorClip((1024,800), color=(0,0,255))

    video = clips_array([[red, green, blue]])

    with pytest.raises(ValueError,
                       message="Expecting ValueError (duration not set)"):
       video.resize(width=480).write_videofile(join(TMP_DIR, "test_clips_array.mp4"))
    video.close()
    red.close()
    green.close()
    blue.close()

def test_clips_array_duration():
    for i in range(20):
        red = ColorClip((1024,800), color=(255,0,0))
        green = ColorClip((1024,800), color=(0,255,0))
        blue = ColorClip((1024,800), color=(0,0,255))

        with clips_array([[red, green, blue]]).set_duration(5) as video:
            with pytest.raises(AttributeError,
                               message="Expecting ValueError (fps not set)"):
                 video.write_videofile(join(TMP_DIR, "test_clips_array.mp4"))


        #this one should work correctly
        red.fps = green.fps = blue.fps = 30

        with clips_array([[red, green, blue]]).set_duration(5) as video:
            video.write_videofile(join(TMP_DIR, "test_clips_array.mp4"))

        red.close()
        green.close()
        blue.close()
