"""TextClip tests."""

import os

import numpy as np

import pytest

from moviepy import *


def test_duration(util):
    clip = TextClip(text="hello world", size=(1280, 720), color="white", font=util.FONT)
    clip = clip.with_duration(5)
    assert clip.duration == 5
    clip.close()

    clip2 = clip.with_effects([vfx.Blink(duration_on=1, duration_off=1)])
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
    expected_error_msg = "^No text nor filename provided$"
    with pytest.raises(ValueError, match=expected_error_msg):
        TextClip(
            size=(20, 20),
            color="#000",
            bg_color="#FFF",
            font=util.FONT,
            method=method,
        )


@pytest.mark.xfail(reason="Autosizing might not work great with new Pillow versions")
def test_label_autosizing(util):
    # We test with about all possible letters
    text = "abcdefghijklmnopqrstuvwxyzáàâäãåāæąēéèêëīíìîïñōóòôöõøœęý\
    ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÂÄÃÅĀÆĄĒÉÈÊËĪÍÌÎÏÑŌÓÒÔÖÕØŒĘÝ"
    text += "\nabcdefghijklmnopqrstuvwxyzáàâäãåāæąēéèêëīíìîïñōóòôöõøœęý\
        ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÂÄÃÅĀÆĄĒÉÈÊËĪÍÌÎÏÑŌÓÒÔÖÕØŒĘÝ"
    text += "\nabcdefghijklmnopqrstuvwxyzáàâäãåāæąēéèêëīíìîïñōóòôöõøœęý\
        ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÂÄÃÅĀÆĄĒÉÈÊËĪÍÌÎÏÑŌÓÒÔÖÕØŒĘÝ"

    text_clip_margin = TextClip(
        util.FONT,
        method="label",
        font_size=40,
        text=text,
        color="red",
        bg_color="black",
        stroke_width=3,
        stroke_color="white",
        margin=(1, 1),
    ).with_duration(1)
    text_clip_no_margin = TextClip(
        util.FONT,
        method="label",
        font_size=40,
        text=text,
        color="red",
        bg_color="black",
        stroke_width=3,
        stroke_color="white",
    ).with_duration(1)

    margin_frame = text_clip_margin.get_frame(1)
    no_margin_frame = text_clip_no_margin.get_frame(1)

    # The idea is, if autosizing work as expected, frame with 1px margin will
    # have black color all around, where frame without margin will have white somewhere
    first_row, last_row = (margin_frame[0], margin_frame[-1])
    first_column, last_column = (margin_frame[:, 0], margin_frame[:, -1])

    # We add a bit of tolerance (about 1%) to account for possible rounding errors
    assert np.allclose(first_row, [0, 0, 0], rtol=0.01)
    assert np.allclose(last_row, [0, 0, 0], rtol=0.01)
    assert np.allclose(first_column, [0, 0, 0], rtol=0.01)
    assert np.allclose(last_column, [0, 0, 0], rtol=0.01)

    # We actually check on three pixels border, because some fonts
    # always add a 1px padding all arround and some rounding error can make it two
    first_three_rows, last_three_rows = (no_margin_frame[:3], no_margin_frame[-3:])
    first_three_columns, last_three_columns = (
        no_margin_frame[:, :3],
        no_margin_frame[:, -3:],
    )

    # We add a bit of tolerance (about 1%) to account for possible rounding errors
    assert not np.allclose(first_three_rows, [0, 0, 0], rtol=0.01)
    assert not np.allclose(last_three_rows, [0, 0, 0], rtol=0.01)
    assert not np.allclose(first_three_columns, [0, 0, 0], rtol=0.01)
    assert not np.allclose(last_three_columns, [0, 0, 0], rtol=0.01)


def test_break_text_wraps_within_width(util):
    """Wrapped caption lines must never exceed the requested width and must
    preserve every word (regression test for absolute-index bug in
    ``__break_text`` that shredded words mid-character after the first line).
    """
    from PIL import Image, ImageDraw, ImageFont

    text = (
        "the quick brown fox jumps over the lazy dog "
        "and then keeps on running far beyond the fence line"
    )
    width = 200
    font_size = 40

    break_text = TextClip._TextClip__break_text
    lines = break_text(
        TextClip.__new__(TextClip),
        width=width,
        text=text,
        font=util.FONT,
        font_size=font_size,
        stroke_width=0,
        align="left",
        spacing=4,
    )

    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    pil_font = ImageFont.truetype(util.FONT, font_size)

    # No line may render wider than the requested width
    for line in lines:
        line_width = draw.textbbox((0, 0), line, font=pil_font)[2]
        assert line_width < width, f"line {line!r} is {line_width}px >= {width}px"

    # No word may be lost, duplicated or split
    assert " ".join(lines).split() == text.split()


def test_no_font(util):
    # Try make a clip with default font
    clip = TextClip(text="Hello world !", font_size=20, color="white")
    clip.show(1)
    assert clip.size[0] > 10


if __name__ == "__main__":
    pytest.main()
