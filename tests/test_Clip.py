import pytest

from moviepy.video.VideoClip import BitmapClip


def test_clip_equality():
    bitmap = [["RR", "RR"], ["RB", "RB"]]
    different_bitmap = [["RR", "RB"], ["RB", "RB"]]

    clip = BitmapClip(bitmap).set_fps(1)
    same_clip = BitmapClip(bitmap).set_fps(1)

    different_clip = BitmapClip(different_bitmap).set_fps(1)

    assert clip == same_clip
    assert clip != different_clip


if __name__ == "__main__":
    pytest.main()
