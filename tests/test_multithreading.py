import sys
from os import path
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import ColorClip
from moviepy.multithreading import multithread_write_videofile


sys.path.append("tests")


def _get_final_clip():
    clip1 = VideoFileClip("media/big_buck_bunny_432_433.webm")
    clip2 = ColorClip((640, 480), color=(255, 0, 0)).set_duration(1)
    final = CompositeVideoClip([clip1, clip2])
    final.fps = 24
    return final


def test_multithread_rendering():
    from test_helper import TMP_DIR
    multithread_write_videofile(
        path.join(TMP_DIR, "test-multithread-rendering.mp4"),
        _get_final_clip)
