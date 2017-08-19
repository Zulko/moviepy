import numpy as np

def supersample(clip, d, nframes):
    """ Replaces each frame at time t by the mean of `nframes` equally spaced frames
    taken in the interval [t-d, t+d]. This results in motion blur."""

    def fl(gf, t):
        lower_bound = t - d
        lower_bound = 0 if lower_bound < 0 else lower_bound
        tt = np.linspace(lower_bound, t+d, nframes)
        avg = np.mean(1.0*np.array([gf(t_) for t_ in tt], dtype='uint16'), axis=0)
        return avg.astype("uint8")

    return clip.fl(fl)
