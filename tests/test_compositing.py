# -*- coding: utf-8 -*-
"""Compositing tests for use with pytest."""
from os.path import join
import sys
import pytest
from moviepy.editor import *
from moviepy.utils import close_all_clips
sys.path.append("tests")
from .test_helper import TMP_DIR


def test_clips_array():
    red = ColorClip((1024, 800), color=(255, 0, 0))
    green = ColorClip((1024, 800), color=(0, 255, 0))
    blue = ColorClip((1024, 800), color=(0, 0, 255))

    video = clips_array([[red, green, blue]])

    with pytest.raises(ValueError,
                       message="Expecting ValueError (duration not set)"):
        video.resize(width=480).write_videofile(
            join(TMP_DIR, "test_clips_array.mp4"))
    close_all_clips(locals())


def test_clips_array_duration():
    # NOTE: anyone knows what behaviour this sets ? If yes please replace
    # this comment.
    red = ColorClip((256, 200), color=(255, 0, 0))
    green = ColorClip((256, 200), color=(0, 255, 0))
    blue = ColorClip((256, 200), color=(0, 0, 255))

    video = clips_array([[red, green, blue]]).set_duration(5)
    with pytest.raises(AttributeError,
                       message="Expecting ValueError (fps not set)"):
        video.write_videofile(join(TMP_DIR, "test_clips_array.mp4"))

    # this one should work correctly
    red.fps = green.fps = blue.fps = 30
    video = clips_array([[red, green, blue]]).set_duration(5)
    video.write_videofile(join(TMP_DIR, "test_clips_array.mp4"))
    close_all_clips(locals())
