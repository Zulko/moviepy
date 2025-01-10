"""Clip tests."""

import copy

import numpy as np

import pytest

from moviepy.Clip import Clip
from moviepy.video.VideoClip import BitmapClip, ColorClip


def test_clip_equality():
    bitmap = [["RR", "RR"], ["RB", "RB"]]
    different_bitmap = [["RR", "RB"], ["RB", "RB"]]
    different_duration_bitmap = [["RR", "RR"], ["RB", "RB"], ["RR", "RR"]]

    clip = BitmapClip(bitmap, fps=1)
    same_clip = BitmapClip(bitmap, fps=1)

    different_clip = BitmapClip(different_bitmap, fps=1)
    different_duration_clip = BitmapClip(different_duration_bitmap, fps=1)

    assert clip == same_clip
    assert clip != different_clip
    assert clip != different_duration_clip
    assert different_clip != different_duration_clip


def test_clip_with_is_mask():
    clip = BitmapClip([["RR", "GG"]], fps=1)
    assert not clip.is_mask

    assert clip.with_is_mask(True).is_mask

    assert not clip.with_is_mask(False).is_mask


@pytest.mark.parametrize(
    (
        "start",
        "end",
        "duration",
        "new_start",
        "change_end",
        "expected_end",
        "expected_duration",
    ),
    (
        (0, 3, 3, 1, True, 4, 3),
        (0, 3, 3, 1, False, 3, 2),  # not change_end
    ),
)
def test_clip_with_start(
    start,
    end,
    duration,
    new_start,
    change_end,
    expected_end,
    expected_duration,
):
    clip = (
        ColorClip(color=(255, 0, 0), size=(2, 2))
        .with_fps(1)
        .with_duration(duration)
        .with_end(end)
        .with_start(start)
    )

    new_clip = clip.with_start(new_start, change_end=change_end)

    assert new_clip.end == expected_end
    assert new_clip.duration == expected_duration


@pytest.mark.parametrize(
    ("duration", "start", "end", "expected_start", "expected_duration"),
    (
        (3, 1, 2, 1, 1),
        (3, 1, None, 1, 3),  # end is None
        (3, None, 4, 1, 3),  # start is None
    ),
)
def test_clip_with_end(duration, start, end, expected_start, expected_duration):
    clip = ColorClip(color=(255, 0, 0), size=(2, 2), duration=duration).with_fps(1)
    if start is not None:
        clip = clip.with_start(start)
    else:
        clip.start = None
    clip = clip.with_end(end)

    assert clip.start == expected_start
    assert clip.duration == expected_duration


@pytest.mark.parametrize(
    (
        "duration",
        "start",
        "end",
        "new_duration",
        "change_end",
        "expected_duration",
        "expected_start",
        "expected_end",
    ),
    (
        (5, None, None, 3, True, 3, 0, 3),
        ("00:00:05", 1, 6, 3, True, 3, 1, 4),  # change end
        ((0, 0, 5), 1, 6, 3, False, 3, 3, 6),  # change start
        (5, None, None, None, False, ValueError, None, None),
    ),
)
def test_clip_with_duration(
    duration,
    start,
    end,
    new_duration,
    change_end,
    expected_duration,
    expected_start,
    expected_end,
):
    clip = ColorClip(color=(255, 0, 0), size=(2, 2)).with_fps(1).with_duration(duration)
    if start is not None:
        clip = clip.with_start(start)
    if end is not None:
        clip = clip.with_end(end)

    if hasattr(expected_duration, "__traceback__"):
        with pytest.raises(expected_duration):
            clip.with_duration(new_duration, change_end=change_end)
    else:
        clip = clip.with_duration(new_duration, change_end=change_end)

        assert clip.duration == expected_duration
        assert clip.start == expected_start
        assert clip.end == expected_end


@pytest.mark.parametrize(
    "copy_func",
    (
        lambda clip: clip.copy(),
        lambda clip: copy.copy(clip),
        lambda clip: copy.deepcopy(clip),
    ),
    ids=(
        "clip.copy()",
        "copy.copy(clip)",
        "copy.deepcopy(clip)",
    ),
)
def test_clip_copy(copy_func):
    """Clip must be copied with `.copy()` method, `copy.copy()` and
    `copy.deepcopy()` (same behaviour).
    """
    clip = Clip()
    other_clip = Clip()

    # shallow copy of clip
    for attr in clip.__dict__:
        setattr(clip, attr, "foo")

    copied_clip = copy_func(clip)

    # assert copied attributes
    for attr in copied_clip.__dict__:
        assert getattr(copied_clip, attr) == getattr(clip, attr)

        # other instances are not edited
        assert getattr(copied_clip, attr) != getattr(other_clip, attr)


@pytest.mark.parametrize(
    ("duration", "start_time", "end_time", "expected_duration"),
    (
        (1, 0, None, 1),
        (3, 0, 2, 2),
        (3, 1, 2, 1),
        (3, -2, 2, 1),  # negative start_time
        (3, 4, None, ValueError),  # start_time > duration
        (3, 3, None, ValueError),  # start_time == duration
        (3, 1, -1, 1),  # negative end_time
        (None, 1, -1, ValueError),  # negative end_time for clip without duration
    ),
)
def test_clip_subclip(duration, start_time, end_time, expected_duration):
    if duration is None:
        clip = ColorClip(color=(255, 0, 0), size=(2, 2)).with_fps(1)
    else:
        clip = BitmapClip([["RR", "GG"] for _ in range(duration)], fps=1)

    if hasattr(expected_duration, "__traceback__"):
        with pytest.raises(expected_duration):
            clip.subclipped(start_time=start_time, end_time=end_time)
    else:
        sub_clip = clip.subclipped(start_time=start_time, end_time=end_time)
        assert sub_clip.duration == expected_duration


@pytest.mark.parametrize(
    ("start_time", "end_time", "expected_frames"),
    (
        (
            1,
            2,
            [["RR", "RR"], ["BB", "BB"]],
        ),
        (
            1,
            3,
            [["RR", "RR"]],
        ),
        (
            2,
            3,
            [["RR", "RR"], ["GG", "GG"]],
        ),
        (
            0,
            1,
            [["GG", "GG"], ["BB", "BB"]],
        ),
        (
            0,
            2,
            [["BB", "BB"]],
        ),
    ),
)
def test_clip_cutout(start_time, end_time, expected_frames):
    clip = BitmapClip([["RR", "RR"], ["GG", "GG"], ["BB", "BB"]], fps=1)
    new_clip = clip.with_section_cut_out(start_time, end_time)

    assert new_clip == BitmapClip(expected_frames, fps=1)


def test_clip_memoize():
    clip = BitmapClip([["RR", "RR"], ["GG", "GG"], ["BB", "BB"]], fps=1)

    assert not clip.memoize

    memoize_clip = clip.with_memoize(True)
    assert memoize_clip.memoize

    # get_frame memoizing
    memoize_clip.memoized_t = 5
    memoize_clip.memoized_frame = "foo"

    assert memoize_clip.get_frame(5) == "foo"

    assert isinstance(memoize_clip.get_frame(1), np.ndarray)


if __name__ == "__main__":
    pytest.main()
