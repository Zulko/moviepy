import pytest
from moviepy.editor import *
import moviepy.video.tools.cuts as cuts

import os
import sys
sys.path.append("tests")
import download_media
from test_helper import PYTHON_VERSION, TMP_DIR, TRAVIS

def test_download_media(capsys):
    with capsys.disabled():
       download_media.download()

def test_matplotlib():
    if PYTHON_VERSION in ('2.7', '3.3'):
       return

    #for now, python 3.5 installs a version of matplotlib that complains
    #about $DISPLAY variable, so lets just ignore for now.
    if PYTHON_VERSION == '3.5' and TRAVIS:
       return

    import matplotlib.pyplot as plt
    import numpy as np
    from moviepy.editor import VideoClip
    from moviepy.video.io.bindings import mplfig_to_npimage

    x = np.linspace(-2, 2, 200)

    duration = 2

    fig, ax = plt.subplots()

    def make_frame(t):
        ax.clear()
        ax.plot(x, np.sinc(x**2) + np.sin(x + 2*np.pi/duration * t), lw=3)
        ax.set_ylim(-1.5, 2.5)
        return mplfig_to_npimage(fig)

    animation = VideoClip(make_frame, duration=duration)
    animation.write_gif(os.path.join(TMP_DIR, 'matplotlib.gif'), fps=20)

if __name__ == '__main__':
   pytest.main()
