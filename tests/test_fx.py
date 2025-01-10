"""MoviePy video and audio effects tests."""

import decimal
import math
import numbers
import os
import random

import numpy as np

import pytest

from moviepy import *
from moviepy.tools import convert_to_seconds


def test_accel_decel():
    pass


def test_blackwhite():
    # Create black/white spectrum ``bw_color_dict`` to compare against it.
    # Colors after ``blackwhite`` FX must be inside this dictionary
    # Note: black/white spectrum is made of colors with same numbers
    # [(0, 0, 0), (1, 1, 1), (2, 2, 2)...]
    bw_color_dict = {}
    for num in range(0, 256):
        bw_color_dict[chr(num + 255)] = (num, num, num)
    color_dict = bw_color_dict.copy()
    # update dictionary with default BitmapClip color_dict values
    color_dict.update(BitmapClip.DEFAULT_COLOR_DICT)

    # add row with random colors in b/w spectrum
    random_row = ""
    for num in range(512, 515):
        # use unique unicode representation for each color
        char = chr(num)
        random_row += char

        # random colors in the b/w spectrum
        color_dict[char] = tuple(random.randint(0, 255) for i in range(3))

    # clip converted below to black/white
    clip = BitmapClip([["RGB", random_row]], color_dict=color_dict, fps=1)

    # for each possible ``preserve_luminosity`` boolean argument value
    for preserve_luminosity in [True, False]:
        # default argument (``RGB=None``)
        clip_bw = clip.with_effects(
            [vfx.BlackAndWhite(preserve_luminosity=preserve_luminosity)]
        )

        bitmap = clip_bw.to_bitmap()
        assert bitmap

        for i, row in enumerate(bitmap[0]):
            for char in row:
                # all characters returned by ``to_bitmap`` are in the b/w spectrum
                assert char in bw_color_dict

                if i == 0:  # pure "RGB" colors are converted to [85, 85, 85]
                    assert char == row[0]  # so are equal

        # custom random ``RGB`` argument
        clip_bw_custom_rgb = clip.with_effects(
            [
                vfx.BlackAndWhite(
                    RGB=(random.randint(0, 255), 0, 0),
                    preserve_luminosity=preserve_luminosity,
                )
            ]
        )
        bitmap = clip_bw_custom_rgb.to_bitmap()
        for i, row in enumerate(bitmap[0]):
            for i2, char in enumerate(row):
                # all characters returned by ``to_bitmap`` are in the b/w spectrum
                assert char in bw_color_dict

                # for clip "RGB" row, two latest converted colors are equal
                if i == 0 and i2 > 0:
                    assert char == row[1] and char == row[2]

        # ``RGB="CRT_phosphor"`` argument
        clip_bw_crt_phosphor = clip.with_effects(
            [
                vfx.BlackAndWhite(
                    RGB="CRT_phosphor", preserve_luminosity=preserve_luminosity
                )
            ]
        )
        bitmap = clip_bw_crt_phosphor.to_bitmap()
        assert bitmap
        for row in bitmap[0]:
            for char in row:
                # all characters returned by ``to_bitmap`` are in the b/w spectrum
                assert char in bw_color_dict


# This currently fails with a with_mask error!
# def test_blink(util):
#     with VideoFileClip("media/big_buck_bunny_0_30.webm").subclip(0,10) as clip:
#       clip1 = blink(clip, 1, 1)
#       clip1.write_videofile(os.path.join(util.TMP_DIR,"blink1.webm"))


def test_multiply_color():
    color_dict = {"H": (0, 0, 200), "L": (0, 0, 50), "B": (0, 0, 255), "O": (0, 0, 0)}
    clip = BitmapClip([["LLO", "BLO"]], color_dict=color_dict, fps=1)

    clipfx = clip.with_effects([vfx.MultiplyColor(4)])
    target = BitmapClip([["HHO", "BHO"]], color_dict=color_dict, fps=1)
    assert target == clipfx


def test_crop():
    # x: 0 -> 4, y: 0 -> 3 inclusive
    clip = BitmapClip([["ABCDE", "EDCBA", "CDEAB", "BAEDC"]], fps=1)

    clip1 = clip.with_effects([vfx.Crop()])
    target1 = BitmapClip([["ABCDE", "EDCBA", "CDEAB", "BAEDC"]], fps=1)
    assert clip1 == target1

    clip2 = clip.with_effects([vfx.Crop(x1=1, y1=1, x2=3, y2=3)])
    target2 = BitmapClip([["DC", "DE"]], fps=1)
    assert clip2 == target2

    clip3 = clip.with_effects([vfx.Crop(y1=2)])
    target3 = BitmapClip([["CDEAB", "BAEDC"]], fps=1)
    assert clip3 == target3

    clip4 = clip.with_effects([vfx.Crop(x1=2, width=2)])
    target4 = BitmapClip([["CD", "CB", "EA", "ED"]], fps=1)
    assert clip4 == target4

    # TODO x_center=1 does not perform correctly
    clip5 = clip.with_effects([vfx.Crop(x_center=2, y_center=2, width=3, height=3)])
    target5 = BitmapClip([["ABC", "EDC", "CDE"]], fps=1)
    assert clip5 == target5

    clip6 = clip.with_effects([vfx.Crop(x_center=2, width=2, y1=1, y2=2)])
    target6 = BitmapClip([["DC"]], fps=1)
    assert clip6 == target6


def test_even_size():
    clip1 = BitmapClip([["ABC", "BCD"]], fps=1)  # Width odd
    clip1even = clip1.with_effects([vfx.EvenSize()])
    target1 = BitmapClip([["AB", "BC"]], fps=1)
    assert clip1even == target1

    clip2 = BitmapClip([["AB", "BC", "CD"]], fps=1)  # Height odd
    clip2even = clip2.with_effects([vfx.EvenSize()])
    target2 = BitmapClip([["AB", "BC"]], fps=1)
    assert clip2even == target2

    clip3 = BitmapClip([["ABC", "BCD", "CDE"]], fps=1)  # Width and height odd
    clip3even = clip3.with_effects([vfx.EvenSize()])
    target3 = BitmapClip([["AB", "BC"]], fps=1)
    assert clip3even == target3


def test_fadein():
    color_dict = {
        "I": (0, 0, 0),
        "R": (255, 0, 0),
        "G": (0, 255, 0),
        "B": (0, 0, 255),
        "W": (255, 255, 255),
    }
    clip = BitmapClip([["R"], ["G"], ["B"]], color_dict=color_dict, fps=1)

    clip1 = clip.with_effects([vfx.FadeIn(1)])  # default initial color
    target1 = BitmapClip([["I"], ["G"], ["B"]], color_dict=color_dict, fps=1)
    assert clip1 == target1

    clip2 = clip.with_effects(
        [vfx.FadeIn(1, initial_color=(255, 255, 255))]
    )  # different initial color
    target2 = BitmapClip([["W"], ["G"], ["B"]], color_dict=color_dict, fps=1)
    assert clip2 == target2


def test_fadeout(util, video):
    clip = video(end_time=0.5)
    clip1 = clip.with_effects([vfx.FadeOut(0.5)])
    clip1.write_videofile(os.path.join(util.TMP_DIR, "fadeout1.webm"))


@pytest.mark.parametrize(
    (
        "t",
        "freeze_duration",
        "total_duration",
        "padding_end",
        "output_frames",
    ),
    (
        # at start, 1 second (default t == 0)
        (
            None,
            1,
            None,
            None,
            ["R", "R", "G", "B"],
        ),
        # at start, 1 second (explicit t)
        (
            0,
            1,
            None,
            None,
            ["R", "R", "G", "B"],
        ),
        # at end, 1 second
        (
            "end",
            1,
            None,
            None,
            ["R", "G", "B", "B"],
        ),
        # at end 1 second, padding end 1 second
        (
            "end",
            1,
            None,
            1,
            ["R", "G", "G", "B"],
        ),
        # at 2nd frame, 1 second
        (
            1,  # second 0 is frame 1, second 1 is frame 2...
            1,
            None,
            None,
            ["R", "G", "G", "B"],
        ),
        # at 2nd frame, 2 seconds
        (
            1,
            2,
            None,
            None,
            ["R", "G", "G", "G", "B"],
        ),
        # `freeze_duration`, `total_duration` are None
        (1, None, None, None, ValueError),
        # `total_duration` 5 at start (2 seconds)
        (None, None, 5, None, ["R", "R", "R", "G", "B"]),
        # total duration 5 at end
        ("end", None, 5, None, ["R", "G", "B", "B", "B"]),
        # total duration 5 padding end
        ("end", None, 5, 1, ["R", "G", "G", "G", "B"]),
    ),
    ids=[
        "at start, 1 second (default t == 0)",
        "at start, 1 second (explicit t)",
        "at end, 1 second",
        "at end 1 second, padding end 1 second",
        "at 2nd frame, 1 second",
        "at 2nd frame, 2 seconds",
        "`freeze_duration`, `total_duration` are None",
        "`total_duration` 5 at start (2 seconds)",
        "`total_duration` 5 at end",
        "`total_duration` 5 padding end",
    ],
)
def test_freeze(t, freeze_duration, total_duration, padding_end, output_frames):
    input_frames = ["R", "G", "B"]
    clip_duration = len(input_frames)

    # create BitmapClip with predefined set of colors, during 1 second each one
    clip = BitmapClip([list(color) for color in input_frames], fps=1).with_duration(
        clip_duration
    )

    # build kwargs passed to `freeze`
    possible_kwargs = {
        "t": t,
        "freeze_duration": freeze_duration,
        "total_duration": total_duration,
        "padding_end": padding_end,
    }
    kwargs = {
        kw_name: kw_value
        for kw_name, kw_value in possible_kwargs.items()
        if kw_value is not None
    }

    # freeze clip
    if hasattr(output_frames, "__traceback__"):
        with pytest.raises(output_frames):
            clip.with_effects([vfx.Freeze(**kwargs)])
        return
    else:
        freezed_clip = clip.with_effects([vfx.Freeze(**kwargs)])

    # assert new duration
    expected_freeze_duration = (
        freeze_duration
        if freeze_duration is not None
        else total_duration - clip_duration
    )
    assert freezed_clip.duration == clip_duration + expected_freeze_duration

    # assert colors are the expected
    for i, color in enumerate(freezed_clip.iter_frames()):
        expected_color = list(BitmapClip.DEFAULT_COLOR_DICT[output_frames[i]])
        assert list(color[0][0]) == expected_color


def test_freeze_region():
    clip = BitmapClip([["AAB", "CCC"], ["BBR", "DDD"], ["CCC", "ABC"]], fps=1)

    # Test region
    clip1 = clip.with_effects([vfx.FreezeRegion(t=1, region=(2, 0, 3, 1))])
    target1 = BitmapClip([["AAR", "CCC"], ["BBR", "DDD"], ["CCR", "ABC"]], fps=1)
    assert clip1 == target1

    # Test outside_region
    clip2 = clip.with_effects([vfx.FreezeRegion(t=1, outside_region=(2, 0, 3, 1))])
    target2 = BitmapClip([["BBB", "DDD"], ["BBR", "DDD"], ["BBC", "DDD"]], fps=1)
    assert clip2 == target2


def test_gamma_corr():
    pass


def test_headblur():
    pass


def test_invert_colors():
    clip = BitmapClip(
        [["AB", "BC"]],
        color_dict={"A": (0, 0, 0), "B": (50, 100, 150), "C": (255, 255, 255)},
        fps=1,
    )

    clip1 = clip.with_effects([vfx.InvertColors()])
    target1 = BitmapClip(
        [["CD", "DA"]],
        color_dict={"A": (0, 0, 0), "D": (205, 155, 105), "C": (255, 255, 255)},
        fps=1,
    )
    assert clip1 == target1


def test_loop(util, video):
    clip = BitmapClip([["R"], ["G"], ["B"]], fps=1)

    clip1 = clip.with_effects([vfx.Loop(n=2)])  # loop 2 times
    target1 = BitmapClip([["R"], ["G"], ["B"], ["R"], ["G"], ["B"]], fps=1)
    assert clip1 == target1

    clip2 = clip.with_effects([vfx.Loop(duration=8)])  # loop 8 seconds
    target2 = BitmapClip(
        [["R"], ["G"], ["B"], ["R"], ["G"], ["B"], ["R"], ["G"]], fps=1
    )
    assert clip2 == target2

    clip3 = clip.with_effects([vfx.Loop()]).with_duration(5)  # infinite loop
    target3 = BitmapClip([["R"], ["G"], ["B"], ["R"], ["G"]], fps=1)
    assert clip3 == target3

    clip = video(start_time=0.2, end_time=0.3)  # 0.1 seconds long
    clip1 = clip.with_effects([vfx.Loop()]).with_duration(0.5)  # infinite looping
    clip1.write_videofile(os.path.join(util.TMP_DIR, "loop1.webm"))

    clip2 = clip.with_effects([vfx.Loop(duration=0.5)])  # loop for 1 second
    clip2.write_videofile(os.path.join(util.TMP_DIR, "loop2.webm"))

    clip3 = clip.with_effects([vfx.Loop(n=3)])  # loop 3 times
    clip3.write_videofile(os.path.join(util.TMP_DIR, "loop3.webm"))

    # Test audio looping
    clip = AudioClip(
        lambda t: np.sin(440 * 2 * np.pi * t) * (t % 1) + 0.5, duration=2.5, fps=44100
    )
    clip1 = clip.with_effects([vfx.Loop(2)])
    # TODO fix AudioClip.__eq__()
    # assert concatenate_audioclips([clip, clip]) == clip1


def test_lum_contrast(util, video):
    clip = video()
    clip1 = clip.with_effects([vfx.LumContrast()])
    clip1.write_videofile(os.path.join(util.TMP_DIR, "lum_contrast1.webm"))

    # what are the correct value ranges for function arguments lum,
    # contrast and contrast_thr?  Maybe we should check for these in
    # lum_contrast.


def test_make_loopable(util, video):
    clip = video()
    clip1 = clip.with_effects([vfx.MakeLoopable(0.4)])

    # We need to set libvpx-vp9 because our test will produce transparency
    clip1.write_videofile(
        os.path.join(util.TMP_DIR, "make_loopable1.webm"), codec="libvpx-vp9"
    )


@pytest.mark.parametrize(
    ("ClipClass"),
    (ColorClip, BitmapClip),
    ids=("ColorClip", "BitmapClip"),
)
@pytest.mark.parametrize(
    (
        "margin_size",
        "margins",  # [left, right, top, bottom]
        "color",
        "expected_result",
    ),
    (
        pytest.param(
            None,
            None,
            None,
            [["RRR", "RRR"], ["RRR", "RRR"]],
            id="default arguments",
        ),
        pytest.param(
            1,
            None,
            None,
            [
                ["OOOOO", "ORRRO", "ORRRO", "OOOOO"],
                ["OOOOO", "ORRRO", "ORRRO", "OOOOO"],
            ],
            id="margin_size=1,color=(0, 0, 0)",
        ),
        pytest.param(
            1,
            None,
            (0, 255, 0),
            [
                ["GGGGG", "GRRRG", "GRRRG", "GGGGG"],
                ["GGGGG", "GRRRG", "GRRRG", "GGGGG"],
            ],
            id="margin_size=1,color=(0, 255, 0)",
        ),
        pytest.param(
            None,
            [1, 0, 0, 0],
            (0, 255, 0),
            [["GRRR", "GRRR"], ["GRRR", "GRRR"]],
            id="left=1,color=(0, 255, 0)",
        ),
        pytest.param(
            None,
            [0, 1, 0, 0],
            (0, 255, 0),
            [["RRRG", "RRRG"], ["RRRG", "RRRG"]],
            id="right=1,color=(0, 255, 0)",
        ),
        pytest.param(
            None,
            [1, 0, 1, 0],
            (0, 255, 0),
            [["GGGG", "GRRR", "GRRR"], ["GGGG", "GRRR", "GRRR"]],
            id="left=1,top=1,color=(0, 255, 0)",
        ),
        pytest.param(
            None,
            [0, 1, 1, 1],
            (0, 255, 0),
            [["GGGG", "RRRG", "RRRG", "GGGG"], ["GGGG", "RRRG", "RRRG", "GGGG"]],
            id="right=1,top=1,bottom=1,color=(0, 255, 0)",
        ),
        pytest.param(
            None,
            [3, 0, 0, 0],
            (255, 255, 255),
            [["WWWRRR", "WWWRRR"], ["WWWRRR", "WWWRRR"]],
            id="left=3,color=(255, 255, 255)",
        ),
        pytest.param(
            None,
            [0, 0, 0, 4],
            (255, 255, 255),
            [
                ["RRR", "RRR", "WWW", "WWW", "WWW", "WWW"],
                ["RRR", "RRR", "WWW", "WWW", "WWW", "WWW"],
            ],
            id="bottom=4,color=(255, 255, 255)",
        ),
    ),
)
def test_margin(ClipClass, margin_size, margins, color, expected_result):
    if ClipClass is BitmapClip:
        clip = BitmapClip([["RRR", "RRR"], ["RRR", "RRR"]], fps=1)
    else:
        clip = ColorClip(color=(255, 0, 0), size=(3, 2), duration=2).with_fps(1)

    # if None, set default argument values
    if color is None:
        color = (0, 0, 0)

    if margins is None:
        margins = [0, 0, 0, 0]
    left, right, top, bottom = margins

    new_clip = clip.with_effects(
        [
            vfx.Margin(
                margin_size=margin_size,
                left=left,
                right=right,
                top=top,
                bottom=bottom,
                color=color,
            )
        ]
    )

    assert new_clip == BitmapClip(expected_result, fps=1)


@pytest.mark.parametrize("image_from", ("np.ndarray", "ImageClip"))
@pytest.mark.parametrize("duration", (None, "random"))
@pytest.mark.parametrize(
    ("color", "mask_color", "expected_color"),
    (
        (
            (0, 0, 0),
            (255, 255, 255),
            (0, 0, 0),
        ),
        (
            (255, 0, 0),
            (0, 0, 255),
            (0, 0, 0),
        ),
        (
            (255, 255, 255),
            (0, 10, 20),
            (0, 10, 20),
        ),
        (
            (10, 10, 10),
            (20, 0, 20),
            (10, 0, 10),
        ),
    ),
)
def test_mask_and(image_from, duration, color, mask_color, expected_color):
    """Checks ``mask_and`` FX behaviour."""
    clip_size = tuple(random.randint(3, 10) for i in range(2))

    if duration == "random":
        duration = round(random.uniform(0, 0.5), 2)

    # test ImageClip and np.ndarray types as mask argument
    clip = ColorClip(color=color, size=clip_size).with_duration(duration)
    mask_clip = ColorClip(color=mask_color, size=clip.size)
    masked_clip = clip.with_effects(
        [
            vfx.MasksAnd(
                mask_clip if image_from == "ImageClip" else mask_clip.get_frame(0)
            )
        ]
    )

    assert masked_clip.duration == clip.duration
    assert np.array_equal(masked_clip.get_frame(0)[0][0], np.array(expected_color))

    # test VideoClip as mask argument
    color_frame, mask_color_frame = (np.array([[color]]), np.array([[mask_color]]))
    clip = VideoClip(lambda t: color_frame).with_duration(duration)
    mask_clip = VideoClip(lambda t: mask_color_frame).with_duration(duration)
    masked_clip = clip.with_effects([vfx.MasksAnd(mask_clip)])

    assert np.array_equal(masked_clip.get_frame(0)[0][0], np.array(expected_color))


def test_mask_color():
    pass


@pytest.mark.parametrize("image_from", ("np.ndarray", "ImageClip"))
@pytest.mark.parametrize("duration", (None, "random"))
@pytest.mark.parametrize(
    ("color", "mask_color", "expected_color"),
    (
        (
            (0, 0, 0),
            (255, 255, 255),
            (255, 255, 255),
        ),
        (
            (255, 0, 0),
            (0, 0, 255),
            (255, 0, 255),
        ),
        (
            (255, 255, 255),
            (0, 10, 20),
            (255, 255, 255),
        ),
        (
            (10, 10, 10),
            (20, 0, 20),
            (20, 10, 20),
        ),
    ),
)
def test_mask_or(image_from, duration, color, mask_color, expected_color):
    """Checks ``mask_or`` FX behaviour."""
    clip_size = tuple(random.randint(3, 10) for i in range(2))

    if duration == "random":
        duration = round(random.uniform(0, 0.5), 2)

    # test ImageClip and np.ndarray types as mask argument
    clip = ColorClip(color=color, size=clip_size).with_duration(duration)
    mask_clip = ColorClip(color=mask_color, size=clip.size)
    masked_clip = clip.with_effects(
        [
            vfx.MasksOr(
                mask_clip if image_from == "ImageClip" else mask_clip.get_frame(0)
            )
        ]
    )

    assert masked_clip.duration == clip.duration
    assert np.array_equal(masked_clip.get_frame(0)[0][0], np.array(expected_color))

    # test VideoClip as mask argument
    color_frame, mask_color_frame = (np.array([[color]]), np.array([[mask_color]]))
    clip = VideoClip(lambda t: color_frame).with_duration(duration)
    mask_clip = VideoClip(lambda t: mask_color_frame).with_duration(duration)
    masked_clip = clip.with_effects([vfx.MasksOr(mask_clip)])

    assert np.array_equal(masked_clip.get_frame(0)[0][0], np.array(expected_color))


def test_mirror_x():
    clip = BitmapClip([["AB", "CD"]], fps=1)
    clip1 = clip.with_effects([vfx.MirrorX()])
    target = BitmapClip([["BA", "DC"]], fps=1)
    assert clip1 == target


def test_mirror_y():
    clip = BitmapClip([["AB", "CD"]], fps=1)
    clip1 = clip.with_effects([vfx.MirrorY()])
    target = BitmapClip([["CD", "AB"]], fps=1)
    assert clip1 == target


def test_painting():
    pass


@pytest.mark.parametrize("apply_to_mask", (True, False))
@pytest.mark.parametrize(
    (
        "size",
        "duration",
        "new_size",
        "width",
        "height",
    ),
    (
        (
            [8, 2],
            1,
            [4, 1],
            None,
            None,
        ),
        (
            [8, 2],
            1,
            None,
            4,
            None,
        ),
        (
            [2, 8],
            1,
            None,
            None,
            4,
        ),
        # neither 'new_size', 'height' or 'width'
        (
            [2, 2],
            1,
            None,
            None,
            None,
        ),
        # `new_size` as scaling factor
        (
            [5, 5],
            1,
            2,
            None,
            None,
        ),
        (
            [5, 5],
            1,
            decimal.Decimal(2.5),
            None,
            None,
        ),
        # arguments as functions
        (
            [2, 2],
            4,
            lambda t: {0: [4, 4], 1: [8, 8], 2: [11, 11], 3: [5, 8]}[t],
            None,
            None,
        ),
        (
            [2, 4],
            2,
            None,
            None,
            lambda t: {0: 3, 1: 4}[t],
        ),
        (
            [5, 2],
            2,
            None,
            lambda t: {0: 3, 1: 4}[t],
            None,
        ),
    ),
)
def test_resize(apply_to_mask, size, duration, new_size, height, width):
    """Checks ``resize`` FX behaviours using all argument"""
    # build expected sizes (using `width` or `height` arguments will be proportional
    # to original size)
    if new_size:
        if hasattr(new_size, "__call__"):
            # function
            expected_new_sizes = [new_size(t) for t in range(duration)]
        elif isinstance(new_size, numbers.Number):
            # scaling factor
            expected_new_sizes = [[int(size[0] * new_size), int(size[1] * new_size)]]
        else:
            # tuple or list
            expected_new_sizes = [new_size]
    elif height:
        if hasattr(height, "__call__"):
            expected_new_sizes = []
            for t in range(duration):
                new_height = height(t)
                expected_new_sizes.append(
                    [int(size[0] * new_height / size[1]), new_height]
                )
        else:
            expected_new_sizes = [[size[0] * height / size[1], height]]
    elif width:
        if hasattr(width, "__call__"):
            expected_new_sizes = []
            for t in range(duration):
                new_width = width(t)
                expected_new_sizes.append(
                    [new_width, int(size[1] * new_width / size[0])]
                )
        else:
            expected_new_sizes = [[width, size[1] * width / size[0]]]
    else:
        expected_new_sizes = None

    clip = ColorClip(size=size, color=(0, 0, 0), duration=duration)
    clip.fps = 1
    mask = ColorClip(size=size, color=0, is_mask=True)
    clip = clip.with_mask(mask)

    # any resizing argument passed, raises `ValueError`
    if expected_new_sizes is None:
        with pytest.raises(ValueError):
            resized_clip = clip.resized(
                new_size=new_size,
                height=height,
                width=width,
                apply_to_mask=apply_to_mask,
            )
        resized_clip = clip
        expected_new_sizes = [size]
    else:
        resized_clip = clip.resized(
            new_size=new_size, height=height, width=width, apply_to_mask=apply_to_mask
        )

    # assert new size for each frame
    for t in range(duration):
        expected_width = expected_new_sizes[t][0]
        expected_height = expected_new_sizes[t][1]

        clip_frame = resized_clip.get_frame(t)

        assert len(clip_frame[0]) == expected_width
        assert len(clip_frame) == expected_height

        mask_frame = resized_clip.mask.get_frame(t)
        if apply_to_mask:
            assert len(mask_frame[0]) == expected_width
            assert len(mask_frame) == expected_height


@pytest.mark.parametrize("unit", ["deg", "rad"])
@pytest.mark.parametrize("resample", ["bilinear", "nearest", "bicubic", "unknown"])
@pytest.mark.parametrize(
    (
        "angle",
        "translate",
        "center",
        "bg_color",
        "expected_frames",
    ),
    (
        (
            0,
            None,
            None,
            None,
            [["AAAA", "BBBB", "CCCC"], ["ABCD", "BCDE", "CDEA"]],
        ),
        (
            90,
            None,
            None,
            None,
            [["ABC", "ABC", "ABC", "ABC"], ["DEA", "CDE", "BCD", "ABC"]],
        ),
        (
            lambda t: 90,
            None,
            None,
            None,
            [["ABC", "ABC", "ABC", "ABC"], ["DEA", "CDE", "BCD", "ABC"]],
        ),
        (
            180,
            None,
            None,
            None,
            [["CCCC", "BBBB", "AAAA"], ["AEDC", "EDCB", "DCBA"]],
        ),
        (
            270,
            None,
            None,
            None,
            [["CBA", "CBA", "CBA", "CBA"], ["CBA", "DCB", "EDC", "AED"]],
        ),
        (
            45,
            (50, 50),
            None,
            (0, 255, 0),
            [
                ["GGGGGG", "GGGGGG", "GGGGGG", "GGGGGG", "GGGGGG", "GGGGGG"],
                ["GGGGGG", "GGGGGG", "GGGGGG", "GGGGGG", "GGGGGG", "GGGGGG"],
            ],
        ),
        (
            45,
            (50, 50),
            (20, 20),
            (255, 0, 0),
            [
                ["RRRRRR", "RRRRRR", "RRRRRR", "RRRRRR", "RRRRRR"],
                ["RRRRRR", "RRRRRR", "RRRRRR", "RRRRRR", "RRRRRR"],
            ],
        ),
        (
            135,
            (-100, -100),
            None,
            (0, 0, 255),
            [
                ["BBBBBB", "BBBBBB", "BBBBBB", "BBBBBB", "BBBBBB"],
                ["BBBBBB", "BBBBBB", "BBBBBB", "BBBBBB", "BBBBBB"],
            ],
        ),
    ),
)
def test_rotate(
    angle,
    unit,
    resample,
    translate,
    center,
    bg_color,
    expected_frames,
):
    """Check ``rotate`` FX behaviour against possible combinations of arguments."""
    original_frames = [["AAAA", "BBBB", "CCCC"], ["ABCD", "BCDE", "CDEA"]]

    # angles are defined in degrees, so convert to radians testing ``unit="rad"``
    if unit == "rad":
        if hasattr(angle, "__call__"):
            _angle = lambda t: math.radians(angle(0))
        else:
            _angle = math.radians(angle)
    else:
        _angle = angle
    clip = BitmapClip(original_frames, fps=1)

    kwargs = {
        "unit": unit,
        "resample": resample,
        "translate": translate,
        "center": center,
        "bg_color": bg_color,
    }
    if resample not in ["bilinear", "nearest", "bicubic"]:
        with pytest.raises(ValueError) as exc:
            clip.rotated(_angle, **kwargs)
        assert (
            "'resample' argument must be either 'bilinear', 'nearest' or 'bicubic'"
        ) == str(exc.value)
        return

    # resolve the angle, because if it is a multiple of 90, the rotation
    # can be computed event without an available PIL installation
    if hasattr(_angle, "__call__"):
        _resolved_angle = _angle(0)
    else:
        _resolved_angle = _angle
    if unit == "rad":
        _resolved_angle = math.degrees(_resolved_angle)

    rotated_clip = clip.with_effects([vfx.Rotate(_angle, **kwargs)])
    expected_clip = BitmapClip(expected_frames, fps=1)

    assert rotated_clip.to_bitmap() == expected_clip.to_bitmap()


def test_rotate_nonstandard_angles(util):
    # Test rotate with color clip
    clip = ColorClip([600, 400], [150, 250, 100]).with_duration(1).with_fps(5)
    clip = clip.with_effects([vfx.Rotate(20)])
    clip.write_videofile(os.path.join(util.TMP_DIR, "color_rotate.webm"))


def test_rotate_mask():
    # Prior to https://github.com/Zulko/moviepy/pull/1399
    # all the pixels of the resulting video were 0
    clip = (
        ColorClip(color=0.5, size=(1, 1), is_mask=True)
        .with_fps(1)
        .with_duration(1)
        .with_effects([vfx.Rotate(45)])
    )
    assert clip.get_frame(0)[1][1] != 0


@pytest.mark.parametrize(
    ("unsupported_kwargs",),
    (
        (["bg_color"],),
        (["center"],),
        (["translate"],),
        (["translate", "center"],),
        (["center", "bg_color", "translate"],),
    ),
    ids=(
        "bg_color",
        "center",
        "translate",
        "translate,center",
        "center,bg_color,translate",
    ),
)
def test_rotate_supported_PIL_kwargs(
    unsupported_kwargs,
    monkeypatch,
):
    """Test supported 'rotate' FX arguments by PIL version."""
    pass


def test_scroll():
    pass


def test_multiply_speed():
    clip = BitmapClip([["A"], ["B"], ["C"], ["D"]], fps=1)

    clip1 = clip.with_effects([vfx.MultiplySpeed(0.5)])  # 1/2x speed
    target1 = BitmapClip(
        [["A"], ["A"], ["B"], ["B"], ["C"], ["C"], ["D"], ["D"]], fps=1
    )
    assert clip1 == target1

    clip2 = clip.with_effects([vfx.MultiplySpeed(final_duration=8)])  # 1/2x speed
    target2 = BitmapClip(
        [["A"], ["A"], ["B"], ["B"], ["C"], ["C"], ["D"], ["D"]], fps=1
    )
    assert clip2 == target2

    clip3 = clip.with_effects([vfx.MultiplySpeed(final_duration=12)])  # 1/2x speed
    target3 = BitmapClip(
        [
            ["A"],
            ["A"],
            ["A"],
            ["B"],
            ["B"],
            ["B"],
            ["C"],
            ["C"],
            ["C"],
            ["D"],
            ["D"],
            ["D"],
        ],
        fps=1,
    )
    assert clip3 == target3

    clip4 = clip.with_effects([vfx.MultiplySpeed(2)])  # 2x speed
    target4 = BitmapClip([["A"], ["C"]], fps=1)
    assert clip4 == target4

    clip5 = clip.with_effects([vfx.MultiplySpeed(final_duration=2)])  # 2x speed
    target5 = BitmapClip([["A"], ["C"]], fps=1)
    assert clip5 == target5

    clip6 = clip.with_effects([vfx.MultiplySpeed(4)])  # 4x speed
    target6 = BitmapClip([["A"]], fps=1)
    assert (
        clip6 == target6
    ), f"{clip6.duration} {target6.duration} {clip6.fps} {target6.fps}"


def test_supersample():
    pass


def test_time_mirror():
    clip = BitmapClip([["AA", "AA"], ["BB", "BB"], ["CC", "CC"]], fps=1)

    clip1 = clip.with_effects([vfx.TimeMirror()])
    target1 = BitmapClip([["CC", "CC"], ["BB", "BB"], ["AA", "AA"]], fps=1)
    assert clip1 == target1

    clip2 = BitmapClip([["AA", "AA"], ["BB", "BB"], ["CC", "CC"], ["DD", "DD"]], fps=1)

    clip3 = clip2.with_effects([vfx.TimeMirror()])
    target3 = BitmapClip(
        [["DD", "DD"], ["CC", "CC"], ["BB", "BB"], ["AA", "AA"]], fps=1
    )
    assert clip3 == target3


def test_time_symmetrize():
    clip = BitmapClip([["AA", "AA"], ["BB", "BB"], ["CC", "CC"]], fps=1)

    clip1 = clip.with_effects([vfx.TimeSymmetrize()])
    target1 = BitmapClip(
        [
            ["AA", "AA"],
            ["BB", "BB"],
            ["CC", "CC"],
            ["CC", "CC"],
            ["BB", "BB"],
            ["AA", "AA"],
        ],
        fps=1,
    )
    assert clip1 == target1


def test_audio_normalize():
    clip = AudioFileClip("media/crunching.mp3")
    clip = clip.with_effects([afx.AudioNormalize()])
    assert clip.max_volume() == 1


def test_audio_normalize_muted():
    z_array = np.array([0.0])
    frame_function = lambda t: z_array
    clip = AudioClip(frame_function, duration=1, fps=44100)
    clip = clip.with_effects([afx.AudioNormalize()])
    assert np.array_equal(clip.to_soundarray(), z_array)


@pytest.mark.parametrize(
    ("sound_type", "factor", "duration", "start_time", "end_time"),
    (
        pytest.param(
            "stereo",
            0,
            None,
            None,
            None,
            id="stereo-0",
        ),
        pytest.param(
            "stereo",
            2,
            None,
            None,
            None,
            id="stereo-2",
        ),
        pytest.param(
            "mono",
            3,
            None,
            None,
            None,
            id="mono-3",
        ),
        pytest.param(
            "stereo",
            0,
            0.2,
            "00:00:00,1",
            None,
            id="stereo-0-start=.1",
        ),
        pytest.param(
            "stereo",
            0,
            0.3,
            None,
            (0, 0, 0.2),
            id="stereo-0-end=.2",
        ),
        pytest.param(
            "stereo",
            0,
            0.3,
            0.1,
            0.2,
            id="stereo-0-start=.1-end=.2",
        ),
        pytest.param(
            "mono",
            0,
            0.3,
            0.2,
            None,
            id="mono-0-start=.2",
        ),
        pytest.param(
            "mono",
            0,
            0.2,
            None,
            "00:00:00.1",
            id="mono-0-end=.1",
        ),
        pytest.param(
            "mono",
            2,
            0.3,
            0.1,
            0.2,
            id="mono-0-start=.1-end=.2",
        ),
    ),
)
def test_multiply_volume_audioclip(
    sound_type,
    factor,
    duration,
    start_time,
    end_time,
):
    if sound_type == "stereo":
        frame_function = lambda t: np.array(
            [
                np.sin(440 * 2 * np.pi * t),
                np.sin(160 * 2 * np.pi * t),
            ]
        ).T.copy(order="C")
    else:
        frame_function = lambda t: [np.sin(440 * 2 * np.pi * t)]

    clip = AudioClip(
        frame_function,
        duration=duration if duration else 0.1,
        fps=22050,
    )
    clip_array = clip.to_soundarray()

    clip_transformed = clip.with_effects(
        [
            afx.MultiplyVolume(
                factor,
                start_time=start_time,
                end_time=end_time,
            )
        ]
    )
    clip_transformed_array = clip_transformed.to_soundarray()

    assert len(clip_transformed_array)

    if hasattr(clip_array, "shape") and len(clip_array.shape) > 1:
        # stereo clip
        left_channel_transformed = clip_transformed_array[:, 0]
        right_channel_transformed = clip_transformed_array[:, 1]

        if start_time is None and end_time is None:
            expected_left_channel_transformed = clip_array[:, 0] * factor
            expected_right_channel_transformed = clip_array[:, 1] * factor
        else:
            start_time = convert_to_seconds(start_time) if start_time else clip.start
            end_time = convert_to_seconds(end_time) if end_time else clip.end

            expected_left_channel_transformed = np.array([])
            expected_right_channel_transformed = np.array([])
            for i, frame in enumerate(clip_array):
                t = i / clip.fps
                transformed_frame = frame * (
                    factor if start_time <= t <= end_time else 1
                )
                expected_left_channel_transformed = np.append(
                    expected_left_channel_transformed,
                    transformed_frame[0],
                )
                expected_right_channel_transformed = np.append(
                    expected_right_channel_transformed,
                    transformed_frame[1],
                )

        assert len(left_channel_transformed)
        assert len(expected_left_channel_transformed)
        assert np.array_equal(
            left_channel_transformed,
            expected_left_channel_transformed,
        )

        assert len(right_channel_transformed)
        assert len(expected_right_channel_transformed)
        assert np.array_equal(
            right_channel_transformed,
            expected_right_channel_transformed,
        )

    else:
        # mono clip

        if start_time is None and end_time is None:
            expected_clip_transformed_array = clip_array * factor
        else:
            start_time = convert_to_seconds(start_time) if start_time else clip.start
            end_time = convert_to_seconds(end_time) if end_time else clip.end

            expected_clip_transformed_array = np.array([])
            for i, frame in enumerate(clip_array[0]):
                t = i / clip.fps
                transformed_frame = frame * (
                    factor if start_time <= t <= end_time else 1
                )
                expected_clip_transformed_array = np.append(
                    expected_clip_transformed_array,
                    transformed_frame,
                )
            expected_clip_transformed_array = np.array(
                [
                    expected_clip_transformed_array,
                ]
            )

        assert len(expected_clip_transformed_array)

        assert np.array_equal(
            expected_clip_transformed_array,
            clip_transformed_array,
        )


def test_multiply_volume_videoclip():
    start_time, end_time = (0.1, 0.2)

    clip = (
        VideoFileClip("media/chaplin.mp4")
        .subclipped(0, 0.3)
        .with_effects(
            [
                afx.MultiplyVolume(
                    0,
                    start_time=start_time,
                    end_time=end_time,
                )
            ]
        )
    )
    clip_soundarray = clip.audio.to_soundarray()

    assert len(clip_soundarray)

    expected_silence = np.zeros(clip_soundarray.shape[1])

    for i, frame in enumerate(clip_soundarray):
        t = i / clip.audio.fps
        if start_time <= t <= end_time:
            assert np.array_equal(frame, expected_silence)
        else:
            assert not np.array_equal(frame, expected_silence)


def test_multiply_stereo_volume():
    clip = AudioFileClip("media/crunching.mp3")

    # stereo mute
    clip_left_channel_muted = clip.with_effects([afx.MultiplyStereoVolume(left=0)])
    clip_right_channel_muted = clip.with_effects(
        [afx.MultiplyStereoVolume(right=0, left=2)]
    )

    left_channel_muted = clip_left_channel_muted.to_soundarray()[:, 0]
    right_channel_muted = clip_right_channel_muted.to_soundarray()[:, 1]

    z_channel = np.zeros(len(left_channel_muted))

    assert np.array_equal(left_channel_muted, z_channel)
    assert np.array_equal(right_channel_muted, z_channel)

    # stereo level doubled
    left_channel_doubled = clip_right_channel_muted.to_soundarray()[:, 0]
    expected_left_channel_doubled = clip.to_soundarray()[:, 0] * 2
    assert np.array_equal(left_channel_doubled, expected_left_channel_doubled)

    # mono muted
    sinus_wave = lambda t: [np.sin(440 * 2 * np.pi * t)]
    mono_clip = AudioClip(sinus_wave, duration=1, fps=22050)
    muted_mono_clip = mono_clip.with_effects([afx.MultiplyStereoVolume(left=0)])
    mono_channel_muted = muted_mono_clip.to_soundarray()

    z_channel = np.zeros(len(mono_channel_muted))
    assert np.array_equal(mono_channel_muted, z_channel)

    # mono doubled
    mono_clip = AudioClip(sinus_wave, duration=1, fps=22050)
    doubled_mono_clip = mono_clip.with_effects(
        [afx.MultiplyStereoVolume(left=None, right=2)]
    )  # using right
    mono_channel_doubled = doubled_mono_clip.to_soundarray()
    d_channel = mono_clip.to_soundarray() * 2
    assert np.array_equal(mono_channel_doubled, d_channel)


@pytest.mark.parametrize(
    ("duration", "offset", "n_repeats", "decay"),
    (
        (0.1, 0.2, 11, 0),
        (0.4, 2, 5, 2),
        (0.5, 0.6, 3, -1),
        (0.3, 1, 7, 4),
    ),
)
def test_audio_delay(stereo_wave, duration, offset, n_repeats, decay):
    """Check that creating a short pulse of audio, the delay converts to a sound
    with the volume level in the form `-_-_-_-_-`, being `-` pulses expressed by
    `duration` argument and `_` being chunks of muted audio. Keep in mind that this
    way of test the FX only works if `duration <= offset`, but as does not make sense
    create a delay with `duration > offset`, this is enough for our purposes.

    Note that decayment values are not tested here, but are created using
    `multiply_volume`, should be OK.
    """
    # limits of this test
    assert n_repeats > 0  # some repetition, if not does not make sense
    assert duration <= offset  # avoid wave distortion
    assert not offset * 1000000 % 2  # odd offset -> no accurate muted chunk size

    # stereo audio clip
    clip = AudioClip(
        frame_function=stereo_wave(left_freq=440, right_freq=880),
        duration=duration,
        fps=44100,
    )
    clip_array = clip.to_soundarray()

    # stereo delayed clip
    delayed_clip = clip.with_effects(
        [afx.AudioDelay(offset=offset, n_repeats=n_repeats, decay=decay)]
    )
    delayed_clip_array = delayed_clip.to_soundarray()

    # size of chunks with audios
    sound_chunk_size = clip_array.shape[0]
    # muted chunks size
    muted_chunk_size = int(sound_chunk_size * offset / duration) - sound_chunk_size

    zeros_expected_chunk_as_muted = np.zeros((muted_chunk_size, 2))

    decayments = np.linspace(1, max(0, decay), n_repeats)

    for i in range(n_repeats + 1):  # first clip, is not part of the repeated ones
        if i == n_repeats:
            # the delay ends in sound, so last muted chunk does not exists
            break

        # sound chunk
        sound_start_at = i * sound_chunk_size + i * muted_chunk_size
        sound_ends_at = sound_start_at + sound_chunk_size

        # first sound chunk
        if i == 0:
            assert np.array_equal(
                delayed_clip_array[:, :][sound_start_at:sound_ends_at],
                clip.with_effects([afx.MultiplyVolume(decayments[i])]).to_soundarray(),
            )

        # muted chunk
        mute_starts_at = sound_ends_at + 1
        mute_ends_at = mute_starts_at + muted_chunk_size

        assert np.array_equal(
            delayed_clip_array[:, :][mute_starts_at:mute_ends_at],
            zeros_expected_chunk_as_muted,
        )

        # check muted bounds
        assert not np.array_equal(
            delayed_clip_array[:, :][mute_starts_at - 1 : mute_ends_at],
            zeros_expected_chunk_as_muted,
        )

        assert not np.array_equal(
            delayed_clip_array[:, :][mute_starts_at : mute_ends_at + 1],
            zeros_expected_chunk_as_muted,
        )


@pytest.mark.parametrize("sound_type", ("stereo", "mono"))
@pytest.mark.parametrize("fps", (44100, 22050))
@pytest.mark.parametrize(
    ("clip_duration", "fadein_duration"),
    (
        (
            (0.2, 0.1),
            (1, "00:00:00,4"),
            (0.3, 0.13),
        )
    ),
)
def test_audio_fadein(
    mono_wave, stereo_wave, sound_type, fps, clip_duration, fadein_duration
):
    if sound_type == "stereo":
        frame_function = stereo_wave(left_freq=440, right_freq=160)
    else:
        frame_function = mono_wave(440)

    clip = AudioClip(frame_function, duration=clip_duration, fps=fps)
    new_clip = clip.with_effects([afx.AudioFadeIn(fadein_duration)])

    # first frame is muted
    first_frame = new_clip.get_frame(0)
    if sound_type == "stereo":
        assert len(first_frame) > 1
        for value in first_frame:
            assert value == 0.0
    else:
        assert first_frame == 0.0

    fadein_duration = convert_to_seconds(fadein_duration)

    n_parts = 10

    # cut transformed part into subclips and check the expected max_volume for
    # each one
    time_foreach_part = fadein_duration / n_parts
    start_times = np.arange(0, fadein_duration, time_foreach_part)
    for i, start_time in enumerate(start_times):
        end_time = start_time + time_foreach_part
        subclip_max_volume = new_clip.subclipped(start_time, end_time).max_volume()

        possible_value = (i + 1) / n_parts
        assert round(subclip_max_volume, 2) in [
            possible_value,
            round(possible_value - 0.01, 5),
        ]

    # cut non transformed part into subclips and check the expected max_volume
    # for each one (almost 1)
    time_foreach_part = (clip_duration - fadein_duration) / n_parts
    start_times = np.arange(fadein_duration, clip_duration, time_foreach_part)
    for i, start_time in enumerate(start_times):
        end_time = start_time + time_foreach_part
        subclip_max_volume = new_clip.subclipped(start_time, end_time).max_volume()

        assert round(subclip_max_volume, 4) == 1


@pytest.mark.parametrize("sound_type", ("stereo", "mono"))
@pytest.mark.parametrize("fps", (44100, 22050))
@pytest.mark.parametrize(
    ("clip_duration", "fadeout_duration"),
    (
        (
            (0.2, 0.1),
            (0.7, "00:00:00,4"),
            (0.3, 0.13),
        )
    ),
)
def test_audio_fadeout(
    mono_wave, stereo_wave, sound_type, fps, clip_duration, fadeout_duration
):
    if sound_type == "stereo":
        frame_function = stereo_wave(left_freq=440, right_freq=160)
    else:
        frame_function = mono_wave(440)

    clip = AudioClip(frame_function, duration=clip_duration, fps=fps)
    new_clip = clip.with_effects([afx.AudioFadeOut(fadeout_duration)])

    fadeout_duration = convert_to_seconds(fadeout_duration)

    n_parts = 10

    # cut transformed part into subclips and check the expected max_volume for
    # each one
    time_foreach_part = fadeout_duration / n_parts
    start_times = np.arange(
        clip_duration - fadeout_duration,
        clip_duration,
        time_foreach_part,
    )
    for i, start_time in enumerate(start_times):
        end_time = start_time + time_foreach_part
        subclip_max_volume = new_clip.subclipped(start_time, end_time).max_volume()

        possible_value = 1 - i * 0.1
        assert round(subclip_max_volume, 2) in [
            round(possible_value, 2),
            round(possible_value - 0.01, 5),
        ]

    # cut non transformed part into subclips and check the expected max_volume
    # for each one (almost 1)
    time_foreach_part = (clip_duration - fadeout_duration) / n_parts
    start_times = np.arange(0, clip_duration - fadeout_duration, time_foreach_part)
    for i, start_time in enumerate(start_times):
        end_time = start_time + time_foreach_part
        subclip_max_volume = new_clip.subclipped(start_time, end_time).max_volume()

        assert round(subclip_max_volume, 4) == 1


if __name__ == "__main__":
    pytest.main()
