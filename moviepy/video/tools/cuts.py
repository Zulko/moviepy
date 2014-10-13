""" This module contains everything that can help automatize
the cuts in MoviePy """

import numpy as np


def find_video_period(clip,fps=None,tmin=.3):
    if fps is None:
        fps=clip.fps
    frame = lambda t: clip.get_frame(t).flatten()
    tt = np.arange(tmin,clip.duration,1.0/ fps)[1:]
    ref = frame(0)
    corrs = [ np.corrcoef(ref, frame(t))[0,1] for t in tt]
    return tt[np.argmax(corrs)]