import pytest
import numpy as np

from moviepy.video.VideoClip import BitmapClip


def test_clip_generation():
    bitmap = [["RR", "RR"], ["RB", "RB"]]
    expected_frame_array = np.array(
        [
            np.array([[(255, 0, 0), (255, 0, 0)], [(255, 0, 0), (255, 0, 0)]]),
            np.array([[(255, 0, 0), (0, 0, 255)], [(255, 0, 0), (0, 0, 255)]]),
        ]
    )
    unexpected_frame_array = np.array(
        [
            np.array([[(255, 0, 0), (255, 0, 0)], [(255, 0, 0), (255, 0, 1)]]),
            np.array([[(255, 0, 0), (0, 0, 255)], [(255, 0, 0), (0, 0, 255)]]),
        ]
    )

    clip = BitmapClip(bitmap)
    clip.duration = len(bitmap)
    clip.fps = 1
    frame_array = np.array(list(clip.iter_frames()))

    # Check that frame_list == expected_frame_list
    assert np.array_equal(frame_array, expected_frame_array)

    # Check that frame_list != unexpected_frame_list
    assert not np.array_equal(frame_array, unexpected_frame_array)


def test_set_fps():
    bitmap = [["R"], ["R"], ["B"], ["B"], ["G"], ["G"]]
    clip = BitmapClip(bitmap)

    fps_clip = clip.set_fps(1)
    assert fps_clip.fps == 1
    assert fps_clip.duration == 6


def test_set_duration():
    bitmap = [["R"], ["R"], ["B"], ["B"], ["G"], ["G"]]
    clip = BitmapClip(bitmap)

    duration_clip = clip.set_duration(len(bitmap))
    assert duration_clip.fps == 1
    assert duration_clip.duration == 6


if __name__ == "__main__":
    test_clip_generation()
    test_set_fps()
    test_set_duration()
