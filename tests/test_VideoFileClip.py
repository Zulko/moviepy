# -*- coding: utf-8 -*-
"""Video file clip tests meant to be run with pytest."""
import os

import pytest

from moviepy.utils import close_all_clips
from moviepy.video.compositing.CompositeVideoClip import clips_array
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ColorClip

from tests.test_helper import TMP_DIR


def test_setup():
    """Test VideoFileClip setup."""
    red = ColorClip((256, 200), color=(255, 0, 0))
    green = ColorClip((256, 200), color=(0, 255, 0))
    blue = ColorClip((256, 200), color=(0, 0, 255))

    red.fps = green.fps = blue.fps = 10
    with clips_array([[red, green, blue]]).set_duration(5) as video:
        video.write_videofile(os.path.join(TMP_DIR, "test.mp4"))

    assert os.path.exists(os.path.join(TMP_DIR, "test.mp4"))

    clip = VideoFileClip(os.path.join(TMP_DIR, "test.mp4"))
    assert clip.duration == 5
    assert clip.fps == 10
    assert clip.size == [256 * 3, 200]
    assert clip.reader.bitrate == 2
    close_all_clips(locals())


def test_ffmpeg_resizing():
    """Test FFmpeg resizing, to include downscaling."""
    video_file = "media/big_buck_bunny_432_433.webm"
    target_resolutions = [(128, 128), (128, None), (None, 128), (None, 256)]
    for target_resolution in target_resolutions:
        video = VideoFileClip(video_file, target_resolution=target_resolution)
        frame = video.get_frame(0)
        for (target, observed) in zip(target_resolution, frame.shape):
            if target is not None:
                assert target == observed
        video.close()


def test_shallow_copy():
    """Call a function which uses @outplace
       and verify that making a shallow copy and deleting it
       does not corrupt the original clip."""
    video_file = "media/big_buck_bunny_0_30.webm"
    video = VideoFileClip(video_file)
    video_copy = video.set_start(1)
    del video_copy
    # The clip object buffers 200000 frames, around 5 seconds ahead.
    # When recentering the buffer, if the new buffer is more than 1000000 frames,
    # around 25s ahead of the end of the current buffer, the reader will
    # reinitialize and fix self.proc.
    # Thus to trigger the bug, you have to look for a frame between ~5 and ~30
    # seconds away. These numbers might vary for different reasons and it would
    # be nice to have a test which was robust to changes in default buffer size, etc.
    video.audio.make_frame(15)


if __name__ == "__main__":
    pytest.main()
