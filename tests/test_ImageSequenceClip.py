"""Image sequencing clip tests meant to be run with pytest."""

import os

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
