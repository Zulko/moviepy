# -*- coding: utf-8 -*-
"""Define general test helper attributes and utilities."""
import os
import sys
import tempfile
import numpy as np

from moviepy.video.VideoClip import VideoClip

TRAVIS = os.getenv("TRAVIS_PYTHON_VERSION") is not None
PYTHON_VERSION = "%s.%s" % (sys.version_info.major, sys.version_info.minor)
TMP_DIR = tempfile.gettempdir()  # because tempfile.tempdir is sometimes None

# Arbitrary font used in caption testing.
if sys.platform in ("win32", "cygwin"):
    FONT = "Arial"
    # Even if Windows users install the Liberation fonts, it is called LiberationMono on Windows, so
    # it doesn't help.
else:
    FONT = (
        "Liberation-Mono"  # This is available in the fonts-liberation package on Linux.
    )


def bitmap_to_frame_list(bitmap_frames, color_dict=None):
    """
    Turns a list of strings into a list of numpy arrays, each letter representing a (r, g, b) tuple.
    Example input (2 frames, 5x3 pixel size):
    [["RRRRR",
      "RRBRR",
      "RRBRR"],
     ["RGGGR",
      "RGGGR",
      "RGGGR"]]
    """
    # "O" represents black
    if color_dict is None:
        color_dict = {
            "R": (255, 0, 0),
            "G": (0, 255, 0),
            "B": (0, 0, 255),
            "O": (0, 0, 0),
            "W": (255, 255, 255),
        }

    output_array = []
    for input_frame in bitmap_frames:
        output_frame = []
        for row in input_frame:
            output_frame.append([color_dict[color] for color in row])
        output_array.append(np.array(output_frame))

    return output_array


def bitmap_to_clip(bitmap_frames, color_dict=None):
    """
    Takes input of the same form as `bitmap_to_frame_list`, but then creates a VideoClip with the
    result. The VideoClip has length in seconds equal to the number of frames, and fps is 1.
    :param bitmap_frames:
    :return:
    """
    frame_list = bitmap_to_frame_list(bitmap_frames, color_dict=color_dict)
    make_frame = lambda t: frame_list[t]
    return VideoClip(make_frame=make_frame, duration=len(frame_list)).set_fps(1)


def clip_to_frame_list(clip):
    """
    Creates a list containing each frame in `clip` as a numpy array.
    """
    li = []
    for t in range(clip.duration * clip.fps):
        frame = clip.get_frame(t)
        li.append(frame)
    return li


def clip_frames_equal(clip1, clip2):
    frames1 = clip_to_frame_list(clip1)
    frames2 = clip_to_frame_list(clip2)
    if len(frames1) != len(frames2):
        print(len(frames1))
        print(len(frames2))
        return False

    for i in range(len(frames1)):
        if not np.array_equal(frames1[i], frames2[i]):
            print(i)
            print(frames1[i])
            print("----------")
            print(frames2[i])
            return False

    return True


def test_bitmap_functions():
    bitmap = [["RR", "RR"], ["RB", "RB"]]
    expected_frame_list = [
        np.array([[(255, 0, 0), (255, 0, 0)], [(255, 0, 0), (255, 0, 0)]]),
        np.array([[(255, 0, 0), (0, 0, 255)], [(255, 0, 0), (0, 0, 255)]]),
    ]
    unexpected_frame_list = [
        np.array([[(255, 0, 0), (255, 0, 0)], [(255, 0, 0), (255, 0, 1)]]),
        np.array([[(255, 0, 0), (0, 0, 255)], [(255, 0, 0), (0, 0, 255)]]),
    ]

    frame_list = bitmap_to_frame_list(bitmap)

    # Check that frame_list == expected_frame_list
    assert len(frame_list) == len(expected_frame_list)
    for i in range(len(frame_list)):
        assert np.array_equal(frame_list[i], expected_frame_list[i])

    # Check that frame_list != unexpected_frame_list
    assert len(frame_list) == len(unexpected_frame_list)
    incorrect_frames = 0
    for i in range(len(frame_list)):
        incorrect_frames += not np.array_equal(frame_list[i], unexpected_frame_list[i])
    assert incorrect_frames == 1


def test_clip_frames_helpers():
    bitmap = [["RR", "RR"], ["RB", "RB"]]
    different_bitmap = [["RR", "RB"], ["RB", "RB"]]

    clip = bitmap_to_clip(bitmap)
    same_clip = bitmap_to_clip(bitmap)

    different_clip = bitmap_to_clip(different_bitmap)

    assert clip_frames_equal(clip, same_clip)
    assert not clip_frames_equal(clip, different_clip)


if __name__ == "__main__":
    test_bitmap_functions()
