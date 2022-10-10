"""TextClip tests."""

import os

import numpy as np

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


def test_text_filename_arguments_consistence(util):
    """Passing ``text`` or ``filename`` we obtain the same result."""
    clip_from_text = (
        TextClip(
            text="Hello",
            size=(20, 20),
            color="#000",
            bg_color="#FFF",
            method="caption",
            font=util.FONT,
        )
        .with_fps(1)
        .with_duration(1)
    )

    with open(os.path.join(util.TMP_DIR, "text-for-clip.txt"), "w") as f:
        f.write("Hello")

    clip_from_file = (
        TextClip(
            text="Hello",
            size=(20, 20),
            color="#000",
            bg_color="#FFF",
            method="caption",
            font=util.FONT,
        )
        .with_fps(1)
        .with_duration(1)
    )

    frames_from_text = list(clip_from_text.iter_frames())
    frames_from_file = list(clip_from_file.iter_frames())
    assert len(frames_from_text) == 1
    assert len(frames_from_file) == 1
    assert np.equal(frames_from_text[0], frames_from_file[0]).all()


@pytest.mark.parametrize(
    "method", ("caption", "label"), ids=("method=caption", "method=label")
)
def test_no_text_nor_filename_arguments(method, util):
    expected_error_msg = (
        "^You must provide either 'text' or 'filename' arguments to TextClip$"
    )
    with pytest.raises(ValueError, match=expected_error_msg):
        TextClip(
            size=(20, 20),
            color="#000",
            bg_color="#FFF",
            font=util.FONT,
            method=method,
        )


if __name__ == "__main__":
    pytest.main()
