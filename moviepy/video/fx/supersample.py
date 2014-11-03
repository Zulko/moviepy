import numpy as np
 
def supersample(clip, d, nframes):
    """ Replaces each frame at time t by the mean of `nframes` equally spaced frames
    taken in the interval [t-d, t+d]. This results in motion blur."""
    
    def fl(gf, t):
        tt = np.linspace(t-d, t+d, nframes)
        avg = np.mean(1.0*np.array([gf(t_) for t_ in tt], dtype='uint16'), axis=0)
        return avg.astype("uint8")

    return clip.fl(fl)