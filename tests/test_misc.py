import os

import pytest

from moviepy.video.tools.cuts import find_video_period
from moviepy.video.fx.resize import resize
from moviepy.utils import close_all_clips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip, file_to_subtitles
from moviepy.video.VideoClip import ColorClip, TextClip

from tests.test_helper import FONT, TMP_DIR


MEDIA_SUBTITLES_DATA = [
    ([0.0, 4.0], "Red!"),
    ([5.0, 9.0], "More Red!"),
    ([10.0, 14.0], "Green!"),
    ([15.0, 19.0], "More Green!"),
    ([20.0, 24.0], "Blue"),
    ([25.0, 29.0], "More Blue!"),
]

MEDIA_SUBTITLES_UNICODE_DATA = [
    ([0, 5.0], "ÁÉíöÙ"),
]


def test_cuts1():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").fx(resize, 0.2)
    find_video_period(clip) == pytest.approx(0.966666666667, 0.0001)
    close_all_clips(locals())


def test_subtitles():
    red = ColorClip((800, 600), color=(255, 0, 0)).with_duration(10)
    green = ColorClip((800, 600), color=(0, 255, 0)).with_duration(10)
    blue = ColorClip((800, 600), color=(0, 0, 255)).with_duration(10)
    myvideo = concatenate_videoclips([red, green, blue])
    assert myvideo.duration == 30

    generator = lambda txt: TextClip(
        txt,
        font=FONT,
        size=(800, 600),
        font_size=24,
        method="caption",
        align="South",
        color="white",
    )

    subtitles = SubtitlesClip("media/subtitles.srt", generator)
    final = CompositeVideoClip([myvideo, subtitles])
    final.write_videofile(os.path.join(TMP_DIR, "subtitles.mp4"), fps=30)

    assert subtitles.subtitles == MEDIA_SUBTITLES_DATA

    subtitles = SubtitlesClip(MEDIA_SUBTITLES_DATA, generator)
    assert subtitles.subtitles == MEDIA_SUBTITLES_DATA
    close_all_clips(locals())


def test_file_to_subtitles():
    assert MEDIA_SUBTITLES_DATA == file_to_subtitles("media/subtitles.srt")


def test_file_to_subtitles_unicode():
    assert MEDIA_SUBTITLES_UNICODE_DATA == file_to_subtitles(
        "media/subtitles-unicode.srt", encoding="utf-8"
    )


if __name__ == "__main__":
    pytest.main()
