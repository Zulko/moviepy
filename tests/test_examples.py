"""MoviePy examples tests."""

import os

import numpy as np

import pytest

from moviepy.video.io.bindings import mplfig_to_npimage
from moviepy.video.VideoClip import VideoClip


try:
    import matplotlib.pyplot
except ImportError:
    matplotlib = None
else:
    matplotlib = True


@pytest.mark.skipif(not matplotlib, reason="no matplotlib")
def test_matplotlib_simple_example(util):
    import matplotlib.pyplot as plt

    plt.switch_backend("Agg")

    x = np.linspace(-2, 2, 200)
    duration = 0.5

    fig, ax = plt.subplots()

    def make_frame(t):
        ax.clear()
        ax.plot(x, np.sinc(x**2) + np.sin(x + 2 * np.pi / duration * t), lw=3)
        ax.set_ylim(-1.5, 2.5)
        return mplfig_to_npimage(fig)

    animation = VideoClip(make_frame, duration=duration)

    filename = os.path.join(util.TMP_DIR, "matplotlib.gif")
    animation.write_gif(filename, fps=20)

    assert os.path.isfile(filename)
