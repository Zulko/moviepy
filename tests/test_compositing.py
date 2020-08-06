# -*- coding: utf-8 -*-
"""Compositing tests for use with pytest."""
from os.path import join

import pytest

from moviepy.editor import *
from moviepy.utils import close_all_clips

from tests.test_helper import TMP_DIR


def test_clips_array():
    red = ColorClip((1024, 800), color=(255, 0, 0))
    green = ColorClip((1024, 800), color=(0, 255, 0))
    blue = ColorClip((1024, 800), color=(0, 0, 255))

    video = clips_array([[red, green, blue]])

    with pytest.raises(ValueError):  # duration not set
        video.resize(width=480).write_videofile(join(TMP_DIR, "test_clips_array.mp4"))
    close_all_clips(locals())


def test_clips_array_duration():
    # NOTE: anyone knows what behaviour this sets ? If yes please replace
    # this comment.
    red = ColorClip((256, 200), color=(255, 0, 0))
    green = ColorClip((256, 200), color=(0, 255, 0))
    blue = ColorClip((256, 200), color=(0, 0, 255))

    video = clips_array([[red, green, blue]]).set_duration(5)
    with pytest.raises(AttributeError):  # fps not set
        video.write_videofile(join(TMP_DIR, "test_clips_array.mp4"))

    # this one should work correctly
    red.fps = green.fps = blue.fps = 30
    video = clips_array([[red, green, blue]]).set_duration(5)
    video.write_videofile(join(TMP_DIR, "test_clips_array.mp4"))
    close_all_clips(locals())


def test_concatenate_self():
    clip = BitmapClip([["AAA", "BBB"], ["CCC", "DDD"]], fps=1)
    target = BitmapClip([["AAA", "BBB"], ["CCC", "DDD"]], fps=1)

    concatenated = concatenate_videoclips([clip])

    concatenated.write_videofile(join(TMP_DIR, "test_concatenate_self.mp4"))
    assert concatenated == target


def test_concatenate_floating_point():
    """
    >>> print("{0:.20f}".format(1.12))
    1.12000000000000010658

    This test uses duration=1.12 to check that it still works when the clip duration is
    represented as being bigger than it actually is. Fixed in #1195.
    """
    clip = ColorClip([100, 50], color=[255, 128, 64], duration=1.12).set_fps(25.0)
    concat = concatenate_videoclips([clip])
    concat.write_videofile("concat.mp4", preset="ultrafast")
