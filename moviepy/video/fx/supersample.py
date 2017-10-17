import numpy as np


def supersample(clip, d, nframes):
    """ Replaces each frame at time t
    by the mean of `nframes` equally spaced frames
    taken in the interval [t-d, t+d]. This results in motion blur."""

    def fl(gf, t):
        # compute times
        lo_bound = t - d
        lo_bound = 0 if lo_bound < 0 else lo_bound
        hi_bound = t + d
        hi_bound = clip.duration - \
            (1 / clip.fps) if hi_bound >= clip.duration else hi_bound
        tt = np.append(np.linspace(lo_bound, hi_bound, nframes - 1), [t])
        # get frames
        frames = [gf(t_) for t_ in tt]
        # compute avg
        frames = np.array(frames, dtype='uint16')
        frames = 1.0 * frames
        avg = np.mean(frames, axis=0)
        return avg.astype("uint8")

    return clip.fl(fl)
