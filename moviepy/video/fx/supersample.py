import numpy as np

def supersample(clip, d, nframes):
    """ Replaces each frame at time t by the mean of `nframes` equally spaced frames
    taken in the interval [t-d, t+d]. This results in motion blur."""

    def fl(gf, t):
        lo_bound = t - d + ((2 * d) / (nframes + 1))
        hi_bound = t + d
        tt = np.linspace(lo_bound, hi_bound, nframes, endpoint=False)
        tt = filter(lambda x: 0 <= x and x < clip.duration, tt)
        avg = np.mean(1.0*np.array([gf(t_) for t_ in tt], dtype='uint16'), axis=0)
        return avg.astype("uint8")

    return clip.fl(fl)
