"""SubtitlesClip tests."""

import os

import pytest

from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.tools.subtitles import SubtitlesClip, file_to_subtitles
from moviepy.video.VideoClip import ColorClip

from tests.test_helper import FONT, TMP_DIR


MEDIA_SUBTITLES_DATA = [
    ([0.0, 1.0], "Red!"),
    ([2.0, 3.5], "More Red!"),
    ([5.0, 6.0], "Green!"),
    ([7.0, 8.0], "Blue"),
    ([9.0, 10.0], "More Blue!"),
]

MEDIA_SUBTITLES_UNICODE_DATA = [
    ([0, 5.0], "ÁÉíöÙ"),
]


def test_subtitles():
    red = ColorClip((800, 600), color=(255, 0, 0)).with_duration(10)
    green = ColorClip((800, 600), color=(0, 255, 0)).with_duration(10)
    blue = ColorClip((800, 600), color=(0, 0, 255)).with_duration(10)
    myvideo = concatenate_videoclips([red, green, blue])
    assert myvideo.duration == 30

    subtitles = SubtitlesClip(
        "media/subtitles.srt", font=FONT, video_width=800, font_size=24, color="white"
    )
    final = CompositeVideoClip([myvideo, subtitles])
    final.subclip(0, 0.5).write_videofile(
        os.path.join(TMP_DIR, "subtitles.mp4"),
        fps=5,
        logger=None,
    )

    assert subtitles.subtitles == MEDIA_SUBTITLES_DATA

    subtitles = SubtitlesClip(
        MEDIA_SUBTITLES_DATA, font=FONT, video_width=800, font_size=24, color="white"
    )
    assert subtitles.subtitles == MEDIA_SUBTITLES_DATA


def test_file_to_subtitles():
    assert MEDIA_SUBTITLES_DATA == file_to_subtitles("media/subtitles.srt")


def test_file_to_subtitles_unicode():
    assert MEDIA_SUBTITLES_UNICODE_DATA == file_to_subtitles(
        "media/subtitles-unicode.srt", encoding="utf-8"
    )


if __name__ == "__main__":
    pytest.main()
