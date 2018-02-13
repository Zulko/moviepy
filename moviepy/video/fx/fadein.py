import numpy as np                                                        

def fadein(clip, duration, initial_color=None):
    """
    Makes the clip progressively appear from some color (black by default),
    over ``duration`` seconds at the beginning of the clip. Can be used for
    masks too, where the initial color must be a number between 0 and 1.
    For cross-fading (progressive appearance or disappearance of a clip
    over another clip, see ``composition.crossfade``
    """

    if initial_color is None:
        initial_color = 0 if clip.ismask else [0,0,0]
    
    initial_color = np.array(initial_color)
    
    def fl(gf, t):
        if t>=duration:
            return gf(t)
        else:
            fading = (1.0*t/duration) 
            return fading*gf(t) + (1-fading)*initial_color

    return clip.fl(fl)