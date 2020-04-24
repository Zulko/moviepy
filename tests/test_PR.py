# -*- coding: utf-8 -*-
"""Pull request tests meant to be run with pytest."""
import os
from pathlib import Path

import pytest

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.utils import close_all_clips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.scroll import scroll
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.tools.interpolators import Trajectory
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.VideoClip import ColorClip, ImageClip, TextClip

from tests.test_helper import FONT, TMP_DIR


def test_PR_306():
    assert TextClip.list("font") != []
    assert TextClip.list("color") != []

    with pytest.raises(Exception):
        TextClip.list("blah")
    close_all_clips(locals())


def test_PR_339():
    # In caption mode.
    TextClip(
        txt="foo",
        color="white",
        font=FONT,
        size=(640, 480),
        method="caption",
        align="center",
        fontsize=25,
    ).close()

    # In label mode.
    TextClip(txt="foo", font=FONT, method="label").close()


def test_PR_373():
    result = Trajectory.load_list("media/traj.txt")

    Trajectory.save_list(result, os.path.join(TMP_DIR, "traj1.txt"))

    result1 = Trajectory.load_list(os.path.join(TMP_DIR, "traj1.txt"))

    assert len(result[0].tt) == len(result1[0].tt)
    for i in range(len(result[0].tt)):
        assert result[0].tt[i] == result1[0].tt[i]

    assert len(result[0].xx) == len(result1[0].xx)
    for i in range(len(result[0].xx)):
        assert result[0].xx[i] == result1[0].xx[i]

    assert len(result[0].yy) == len(result1[0].yy)
    for i in range(len(result[0].yy)):
        assert result[0].yy[i] == result1[0].yy[i]


def test_PR_458():
    clip = ColorClip([1000, 600], color=(60, 60, 60), duration=2)
    clip.write_videofile(os.path.join(TMP_DIR, "test.mp4"), logger=None, fps=30)
    clip.close()


def test_PR_515():
    # Won't actually work until video is in download_media
    with VideoFileClip("media/fire2.mp4", fps_source="tbr") as clip:
        assert clip.fps == 90000
    with VideoFileClip("media/fire2.mp4", fps_source="fps") as clip:
        assert clip.fps == 10.51


def test_PR_528():
    with ImageClip("media/vacation_2017.jpg") as clip:
        new_clip = scroll(clip, w=1000, x_speed=50)
        new_clip = new_clip.set_duration(1)
        new_clip.fps = 24
        new_clip.write_videofile(os.path.join(TMP_DIR, "pano.mp4"))


def test_PR_529():
    with VideoFileClip("media/fire2.mp4") as video_clip:
        assert video_clip.rotation == 180


def test_PR_610():
    """
    Test that the max fps of the video clips is used for the composite video clip
    """
    clip1 = ColorClip((640, 480), color=(255, 0, 0)).set_duration(1)
    clip2 = ColorClip((640, 480), color=(0, 255, 0)).set_duration(1)
    clip1.fps = 24
    clip2.fps = 25
    composite = CompositeVideoClip([clip1, clip2])
    assert composite.fps == 25


def test_PR_1137_video():
    """
    Test support for path-like objects as arguments for VideoFileClip.
    """
    with VideoFileClip(Path("media/big_buck_bunny_432_433.webm")) as video:
        video.write_videofile(Path(TMP_DIR) / "pathlike.mp4")
        assert isinstance(video.filename, str)


def test_PR_1137_audio():
    """
    Test support for path-like objects as arguments for AudioFileClip.
    """
    with AudioFileClip(Path("media/crunching.mp3")) as audio:
        audio.write_audiofile(Path(TMP_DIR) / "pathlike.mp3")
        assert isinstance(audio.filename, str)


def test_PR_1137_image():
    """
    Test support for path-like objects as arguments for ImageClip.
    """
    ImageClip(Path("media/vacation_2017.jpg")).close()


def test_PR_1137_subtitles():
    """
    Test support for path-like objects as arguments for SubtitlesClip.
    """

    def make_textclip(txt):
        return TextClip(
            txt,
            font=FONT,
            fontsize=24,
            color="white",
            stroke_color="black",
            stroke_width=0.5,
        )

    SubtitlesClip(Path("media/subtitles1.srt"), make_textclip=make_textclip).close()


if __name__ == "__main__":
    pytest.main()
