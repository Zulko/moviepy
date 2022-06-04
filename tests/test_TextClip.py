"""TextClip tests."""

import os
import tempfile

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


@pytest.mark.xfail(raises=AssertionError)
def test_textclip_filename_parameter_actually_work(util):
    """
    Regardless you provide a filename or text paramter,
    the final text attribute should be of the format @<file_name>
    not @%<file_name> which is how it's set before this fix.
    """
    # Create the temp text file to make sure we know
    # the exact name to use it later when checking
    # both methods result in the same parameter value
    tempfile_fd, temp_text_filename = tempfile.mkstemp(suffix=".txt")
    os.close(tempfile_fd)

    text_clip_with_text = TextClip(
        text="foo",
        temptxt=temp_text_filename,
        method="caption",
        size=(220, 134),
        font=util.FONT,
    )
    text_clip_with_file = TextClip(
        filename=temp_text_filename,
        method="caption",
        size=(220, 134),
        font=util.FONT,
    )

    assert text_clip_with_file.text == text_clip_with_text.text

    text_clip_with_file.close()
    text_clip_with_text.close()

    os.remove(temp_text_filename)


if __name__ == "__main__":
    pytest.main()
