# -*- coding: utf-8 -*-
"""Video file clip tests meant to be run with pytest."""
import os
import sys

import pytest
from moviepy.video.compositing.CompositeVideoClip import clips_array
from moviepy.video.VideoClip import ColorClip
from moviepy.video.io.VideoFileClip import VideoFileClip

sys.path.append("tests")
from test_helper import TMP_DIR

def test_setup():
    """Test VideoFileClip setup."""
    red = ColorClip((1024,800), color=(255,0,0))
    green = ColorClip((1024,800), color=(0,255,0))
    blue = ColorClip((1024,800), color=(0,0,255))

    red.fps = green.fps = blue.fps = 30
    with clips_array([[red, green, blue]]).set_duration(5) as video:
        video.write_videofile(os.path.join(TMP_DIR, "test.mp4"))

    assert os.path.exists(os.path.join(TMP_DIR, "test.mp4"))

    with VideoFileClip(os.path.join(TMP_DIR, "test.mp4")) as clip:
        assert clip.duration == 5
        assert clip.fps == 30
        assert clip.size == [1024*3, 800]

    red.close()
    green.close()
    blue.close()

def test_ffmpeg_resizing():
    """Test FFmpeg resizing, to include downscaling."""
    video_file = 'media/big_buck_bunny_432_433.webm'
    target_resolution = (128, 128)
    with VideoFileClip(video_file, target_resolution=target_resolution) as video:
        frame = video.get_frame(0)
        assert frame.shape[0:2] == target_resolution

    target_resolution = (128, None)
    with VideoFileClip(video_file, target_resolution=target_resolution) as video:
        frame = video.get_frame(0)
        assert frame.shape[0] == target_resolution[0]

    target_resolution = (None, 128)
    with VideoFileClip(video_file, target_resolution=target_resolution) as video:
        frame = video.get_frame(0)
        assert frame.shape[1] == target_resolution[1]

    # Test upscaling
    target_resolution = (None, 2048)
    with VideoFileClip(video_file, target_resolution=target_resolution) as video:
        frame = video.get_frame(0)
        assert frame.shape[1] == target_resolution[1]


if __name__ == '__main__':
   pytest.main()
