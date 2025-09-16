"""Image sequencing clip tests meant to be run with pytest."""

import os

import numpy as np

import pytest

from moviepy.video.io.ImageSequenceClip import ImageSequenceClip


def test_1(util):
    images = []
    durations = []

    for i in range(5):
        durations.append(i)
        images.append("media/python_logo.png")
        durations.append(i)
        images.append("media/python_logo_upside_down.png")

    with ImageSequenceClip(images, durations=durations) as clip:
        assert clip.duration == sum(durations)
        clip.write_videofile(
            os.path.join(util.TMP_DIR, "ImageSequenceClip1.mp4"), fps=30, logger=None
        )


def test_2():
    images = []
    durations = []

    durations.append(1)
    images.append("media/python_logo.png")
    durations.append(2)
    images.append("media/matplotlib_demo1.png")

    # images are not the same size..
    with pytest.raises(Exception):
        ImageSequenceClip(images, durations=durations).close()


if __name__ == "__main__":
    pytest.main()


def test_no_repeat_frames():
    # set of frames that are all different levels of grey
    frames = [np.ones((400, 400, 3)) * f for f in np.linspace(0, 1, 20)]

    for frames_per_second in range(1, 31):
        movie = ImageSequenceClip(frames, fps=frames_per_second)
        c = np.array([f[0, 0, 0] for f in movie.iter_frames()])
        assert np.all(c[1:] != c[:-1])


def test_correct_number_of_frames():
    # set of frames that are all different levels of grey
    frames = [np.ones((400, 400, 3)) * f for f in np.linspace(0, 1, 20)]

    for frames_per_second in range(1, 31):
        movie = ImageSequenceClip(frames, fps=frames_per_second)
        c = np.array([f[0, 0, 0] for f in movie.iter_frames()])
        assert len(c) == 20
