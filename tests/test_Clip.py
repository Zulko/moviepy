import copy

import pytest

from moviepy.Clip import Clip
from moviepy.video.VideoClip import BitmapClip


def test_clip_equality():
    bitmap = [["RR", "RR"], ["RB", "RB"]]
    different_bitmap = [["RR", "RB"], ["RB", "RB"]]

    clip = BitmapClip(bitmap, fps=1)
    same_clip = BitmapClip(bitmap, fps=1)

    different_clip = BitmapClip(different_bitmap, fps=1)

    assert clip == same_clip
    assert clip != different_clip


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


if __name__ == "__main__":
    pytest.main()
