"""Pull request tests meant to be run with pytest."""

import os
from pathlib import Path

import pytest

from moviepy import *
from moviepy.video.tools.interpolators import Trajectory
from moviepy.video.tools.subtitles import SubtitlesClip


def test_PR_339(util):
    # In caption mode.
    TextClip(
        font=util.FONT,
        text="foo",
        color="white",
        size=(640, 480),
        method="caption",
        text_align="center",
        font_size=25,
    ).close()

    # In label mode.
    TextClip(text="foo", font=util.FONT, method="label", font_size=25).close()


def test_PR_373(util):
    result = Trajectory.load_list("media/traj.txt")

    Trajectory.save_list(result, os.path.join(util.TMP_DIR, "traj1.txt"))

    result1 = Trajectory.load_list(os.path.join(util.TMP_DIR, "traj1.txt"))

    assert len(result[0].tt) == len(result1[0].tt)
    for i in range(len(result[0].tt)):
        assert result[0].tt[i] == result1[0].tt[i]

    assert len(result[0].xx) == len(result1[0].xx)
    for i in range(len(result[0].xx)):
        assert result[0].xx[i] == result1[0].xx[i]

    assert len(result[0].yy) == len(result1[0].yy)
    for i in range(len(result[0].yy)):
        assert result[0].yy[i] == result1[0].yy[i]


def test_PR_458(util):
    clip = ColorClip([1000, 600], color=(60, 60, 60), duration=2)
    clip.write_videofile(os.path.join(util.TMP_DIR, "test.mp4"), logger=None, fps=30)
    clip.close()


def test_PR_515():
    # Won't actually work until video is in download_media
    with VideoFileClip("media/fire2.mp4", fps_source="tbr") as clip:
        assert clip.fps == 90000
    with VideoFileClip("media/fire2.mp4", fps_source="fps") as clip:
        assert clip.fps == 10.51


def test_PR_528(util):
    with ImageClip("media/vacation_2017.jpg") as clip:
        new_clip = clip.with_effects([vfx.Scroll(w=1000, x_speed=50)])
        new_clip = new_clip.with_duration(0.2)
        new_clip.fps = 24
        new_clip.write_videofile(os.path.join(util.TMP_DIR, "pano.mp4"), logger=None)


def test_PR_529():
    with VideoFileClip("media/fire2.mp4") as video_clip:
        assert video_clip.rotation == 180


def test_PR_610():
    """Test that the max fps of video clips is used for the composite video clip."""
    clip1 = ColorClip((640, 480), color=(255, 0, 0)).with_duration(1)
    clip2 = ColorClip((640, 480), color=(0, 255, 0)).with_duration(1)
    clip1.fps = 24
    clip2.fps = 25
    composite = CompositeVideoClip([clip1, clip2])
    assert composite.fps == 25


def test_PR_1137_video(util, video):
    """Test support for path-like objects as arguments for VideoFileClip."""
    with video(start_time=0.2, end_time=0.24) as video:
        video.write_videofile(Path(util.TMP_DIR) / "pathlike.mp4", logger=None)
        assert isinstance(video.filename, str)


def test_PR_1137_audio(util):
    """Test support for path-like objects as arguments for AudioFileClip."""
    with AudioFileClip(Path("media/crunching.mp3")) as audio:
        audio.write_audiofile(Path(util.TMP_DIR) / "pathlike.mp3")
        assert isinstance(audio.filename, str)


def test_PR_1137_image():
    """Test support for path-like objects as arguments for ImageClip."""
    ImageClip(Path("media/vacation_2017.jpg")).close()


def test_PR_1137_subtitles(util):
    """Test support for path-like objects as arguments for SubtitlesClip."""

    def make_textclip(txt):
        return TextClip(
            font=util.FONT,
            text=txt,
            font_size=24,
            color="white",
            stroke_color="black",
            stroke_width=1,
        )

    SubtitlesClip(Path("media/subtitles.srt"), make_textclip=make_textclip).close()


if __name__ == "__main__":
    pytest.main()
