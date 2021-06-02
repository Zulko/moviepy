"""TextClip tests."""

import pytest

from moviepy.video.fx.blink import blink
from moviepy.video.VideoClip import TextClip


def test_list():
    fonts = TextClip.list("font")
    assert isinstance(fonts, list)
    assert isinstance(fonts[0], str)

    colors = TextClip.list("color")
    assert isinstance(colors, list)
    assert isinstance(colors[0], str)
    assert "blue" in colors


def test_search():
    blues = TextClip.search("blue", "color")
    assert isinstance(blues, list)
    assert isinstance(blues[0], str)
    assert "blue" in blues


def test_duration(util):
    clip = TextClip("hello world", size=(1280, 720), color="white", font=util.FONT)
    clip = clip.with_duration(5)
    assert clip.duration == 5
    clip.close()

    clip2 = clip.fx(blink, duration_on=1, duration_off=1)
    clip2 = clip2.with_duration(5)
    assert clip2.duration == 5


# Moved from tests.py. Maybe we can remove these?
def test_if_textclip_crashes_in_caption_mode(util):
    TextClip(
        text="foo",
        color="white",
        size=(640, 480),
        method="caption",
        align="center",
        font_size=25,
        font=util.FONT,
    ).close()


def test_if_textclip_crashes_in_label_mode(util):
    TextClip(text="foo", method="label", font=util.FONT).close()


if __name__ == "__main__":
    pytest.main()
