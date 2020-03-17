# -*- coding: utf-8 -*-
import os

import pytest
import numpy as np
try:
	import matplotlib
except ImportError:
	matplotlib = None
from moviepy.video.io.bindings import mplfig_to_npimage
from moviepy.video.VideoClip import VideoClip
from .test_helper import PYTHON_VERSION, TMP_DIR, TRAVIS


@pytest.mark.skipif(not matplotlib, reason="no mpl") 
@pytest.mark.skipif(PYTHON_VERSION in ('2.7', '3.3'), reason="version")
@pytest.mark.skipif(PYTHON_VERSION == '3.5' and TRAVIS, reason="travis py35")
def test_matplotlib():
    #for now, python 3.5 installs a version of matplotlib that complains
    #about $DISPLAY variable, so lets just ignore for now.
    
    x = np.linspace(-2, 2, 200)

    duration = 2

    matplotlib.use('Agg')
    fig, ax = matplotlib.pyplot.subplots()

    def make_frame(t):
        ax.clear()
        ax.plot(x, np.sinc(x**2) + np.sin(x + 2*np.pi/duration * t), lw=3)
        ax.set_ylim(-1.5, 2.5)
        return mplfig_to_npimage(fig)

    animation = VideoClip(make_frame, duration=duration)
    animation.write_gif(os.path.join(TMP_DIR, 'matplotlib.gif'), fps=20)
