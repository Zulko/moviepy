"""Compositing tests for use with pytest."""

import os

import numpy as np

import pytest

from moviepy import *


class ClipPixelTest:
    ALLOWABLE_COLOR_VARIATION = 3  # from 0-767: how much mismatch do we allow

    def __init__(self, clip):
        self.clip = clip

    def expect_color_at(self, ts, expected, xy=[0, 0]):
        frame = self.clip.frame_function(ts)
        r, g, b = expected
        actual = frame[xy[1]][xy[0]]
        diff = abs(actual[0] - r) + abs(actual[1] - g) + abs(actual[2] - b)

        mismatch = diff > ClipPixelTest.ALLOWABLE_COLOR_VARIATION
        assert (
            not mismatch
        ), "Expected (%02x,%02x,%02x) but got (%02x,%02x,%02x) at timestamp %s" % (
            *expected,
            *actual,
            ts,
        )


def test_clips_array(util):
    red = ColorClip((1024, 800), color=(255, 0, 0))
    green = ColorClip((1024, 800), color=(0, 255, 0))
    blue = ColorClip((1024, 800), color=(0, 0, 255))

    video = clips_array([[red, green, blue]])

    with pytest.raises(ValueError):  # duration not set
        video.with_effects([vfx.Resize(width=480)]).write_videofile(
            os.path.join(util.TMP_DIR, "test_clips_array.mp4")
        )


def test_clips_array_duration(util):
    filename = os.path.join(util.TMP_DIR, "test_clips_array.mp4")

    # NOTE: anyone knows what behaviour this sets ? If yes please replace
    # this comment.
    red = ColorClip((256, 200), color=(255, 0, 0))
    green = ColorClip((256, 200), color=(0, 255, 0))
    blue = ColorClip((256, 200), color=(0, 0, 255))

    video = clips_array([[red, green, blue]]).with_duration(5)
    with pytest.raises(AttributeError):  # fps not set
        video.write_videofile(filename)

    # this one should work correctly
    red.fps = green.fps = blue.fps = 30
    video = clips_array([[red, green, blue]]).with_duration(5)
    video.write_videofile(filename)


def test_concatenate_self(util):
    clip = BitmapClip([["AAA", "BBB"], ["CCC", "DDD"]], fps=1)
    target = BitmapClip([["AAA", "BBB"], ["CCC", "DDD"]], fps=1)

    concatenated = concatenate_videoclips([clip])

    concatenated.write_videofile(
        os.path.join(util.TMP_DIR, "test_concatenate_self.mp4")
    )
    assert concatenated == target


def test_concatenate_floating_point(util):
    """
    >>> print("{0:.20f}".format(1.12))
    1.12000000000000010658

    This test uses duration=1.12 to check that it still works when the clip
    duration is represented as being bigger than it actually is. Fixed in #1195.
    """
    clip = ColorClip([100, 50], color=[255, 128, 64], duration=1.12).with_fps(25.0)
    concat = concatenate_videoclips([clip])
    concat.write_videofile(os.path.join(util.TMP_DIR, "concat.mp4"), preset="ultrafast")


def test_blit_with_opacity():
    # has one second R, one second G, one second B
    size = (2, 2)
    clip1 = (
        ColorClip(size, color=(255, 0, 0), duration=1)
        + ColorClip(size, color=(0, 255, 0), duration=1)
        + ColorClip(size, color=(0, 0, 255), duration=1)
    )

    # overlay green at half opacity during first 2 sec
    clip2 = ColorClip(size, color=(0, 255, 0), duration=2).with_opacity(0.5)
    composite = CompositeVideoClip([clip1, clip2])
    bt = ClipPixelTest(composite)

    # red + 50% green
    bt.expect_color_at(0.5, (0x7F, 0x7F, 0x00))
    # green + 50% green
    bt.expect_color_at(1.5, (0x00, 0xFF, 0x00))
    # blue is after 2s, so keep untouched
    bt.expect_color_at(2.5, (0x00, 0x00, 0xFF))


def test_compositing_masks(util):
    # Has one R 30%, one G 30%, one B 30%
    clip1 = ColorClip((100, 100), (255, 0, 0, 76.5)).with_duration(2)
    clip2 = ColorClip((50, 50), (0, 255, 0, 76.5)).with_duration(2)
    clip3 = ColorClip((25, 25), (0, 0, 255, 76.5)).with_duration(2)

    compostite_clip1 = CompositeVideoClip(
        [clip1, clip2.with_position(("center", "center"))]
    )
    compostite_clip2 = CompositeVideoClip(
        [compostite_clip1, clip3.with_position(("center", "center"))]
    )

    # Load output file and check transparency
    frame = compostite_clip2.mask.get_frame(1)

    # We check opacity with one, two and three layers
    # Allow for a bit of tolerance (about 1%) to account
    # for rounding errors
    opacity1 = frame[50, 10]
    opacity2 = frame[50, 30]
    opacity3 = frame[50, 50]
    assert abs(opacity1 - 0.3) < 0.01
    assert abs(opacity2 - 0.51) < 0.01
    assert abs(opacity3 - 0.657) < 0.01


def test_compositing_with_transparency_colors(util):
    # Has one R 30%, one G 30%, one B 30%
    clip1 = ColorClip((100, 100), (255, 0, 0, 76.5)).with_duration(2)
    clip2 = ColorClip((50, 50), (0, 255, 0, 76.5)).with_duration(2)
    clip3 = ColorClip((25, 25), (0, 0, 255, 76.5)).with_duration(2)

    compostite_clip1 = CompositeVideoClip(
        [clip1, clip2.with_position(("center", "center"))]
    )
    compostite_clip2 = CompositeVideoClip(
        [compostite_clip1, clip3.with_position(("center", "center"))]
    )

    # Load output file and check transparency
    frame = compostite_clip2.get_frame(1)
    mask = compostite_clip2.mask.get_frame(1)

    # We check color with 1 layer
    # We add a bit of tolerance (about 1%) to account
    # For possible rounding errors
    color1 = frame[50, 10]
    opacity1 = mask[50, 10]
    assert np.allclose(color1, [255, 0, 0], rtol=0.01)
    assert abs(opacity1 - 0.3) < 0.01

    # With 2 layers
    color2 = frame[50, 30]
    opacity2 = mask[50, 30]
    assert np.allclose(color2, [105, 150, 0], rtol=0.01)
    assert abs(opacity2 - 0.51) < 0.01

    # With 3 layers
    color3 = frame[50, 50]
    opacity3 = mask[50, 50]
    assert np.allclose(color3, [57, 82, 116], rtol=0.01)
    assert abs(opacity3 - 0.657) < 0.01


def test_slide_in():
    duration = 0.1
    size = (10, 1)
    fps = 10
    color = (255, 0, 0)

    # left and right sides
    clip = ColorClip(
        color=color,
        duration=duration,
        size=size,
    ).with_fps(fps)

    for side in ["left", "right"]:
        new_clip = CompositeVideoClip(
            [clip.with_effects([vfx.SlideIn(duration, side)])]
        )

        for t in np.arange(0, duration, duration / fps):
            n_reds, n_reds_expected = (0, int(t * 100))

            if t:
                assert n_reds_expected

            if n_reds_expected == 7:  # skip 7 due to inaccurate frame
                continue

            for r, g, b in new_clip.get_frame(t)[0]:
                if r == color[0] and g == color[1] and g == color[2]:
                    n_reds += 1

            assert n_reds == n_reds_expected

    # top and bottom sides
    clip = ColorClip(
        color=color,
        duration=duration,
        size=(size[1], size[0]),
    ).with_fps(fps)

    for side in ["top", "bottom"]:
        new_clip = CompositeVideoClip(
            [clip.with_effects([vfx.SlideIn(duration, side)])]
        )
        for t in np.arange(0, duration, duration / fps):
            n_reds, n_reds_expected = (0, int(t * 100))

            if t:
                assert n_reds_expected

            if n_reds_expected == 7:  # skip 7 due to inaccurate frame
                continue

            for row in new_clip.get_frame(t):
                r, g, b = row[0]

                if r == color[0] and g == color[1] and g == color[2]:
                    n_reds += 1

            assert n_reds == n_reds_expected


def test_slide_out():
    duration = 0.1
    size = (11, 1)
    fps = 10
    color = (255, 0, 0)

    # left and right sides
    clip = ColorClip(
        color=color,
        duration=duration,
        size=size,
    ).with_fps(fps)

    for side in ["left", "right"]:
        new_clip = CompositeVideoClip(
            [clip.with_effects([vfx.SlideOut(duration, side)])]
        )

        for t in np.arange(0, duration, duration / fps):
            n_reds, n_reds_expected = (0, round(11 - t * 100, 6))

            if t:
                assert n_reds_expected

            for r, g, b in new_clip.get_frame(t)[0]:
                if r == color[0] and g == color[1] and g == color[2]:
                    n_reds += 1

            assert n_reds == n_reds_expected

    # top and bottom sides
    clip = ColorClip(
        color=color,
        duration=duration,
        size=(size[1], size[0]),
    ).with_fps(fps)

    for side in ["top", "bottom"]:
        new_clip = CompositeVideoClip(
            [clip.with_effects([vfx.SlideOut(duration, side)])]
        )
        for t in np.arange(0, duration, duration / fps):
            n_reds, n_reds_expected = (0, round(11 - t * 100, 6))

            if t:
                assert n_reds_expected

            for row in new_clip.get_frame(t):
                r, g, b = row[0]

                if r == color[0] and g == color[1] and g == color[2]:
                    n_reds += 1

            assert n_reds == n_reds_expected


def test_concatenate_with_masks(util):
    video_without_mask = (
        ColorClip(size=(10, 10), color=(255, 0, 0)).with_duration(1).with_fps(1)
    )
    video_with_mask = (
        ColorClip(size=(5, 5), color=(0, 255, 0))
        .with_duration(1)
        .with_fps(1)
        .with_mask()
    )

    output = os.path.join(util.TMP_DIR, "test_concatenate_with_masks.mp4")
    concatenate_videoclips([video_without_mask, video_with_mask]).write_videofile(
        output
    )


if __name__ == "__main__":
    pytest.main()
