import numpy as np

def mask_color(clip, color=None, thr=0, s=1):
    """ Returns a new clip with a mask for transparency where the original
    clip is of the given color.

    You can also have a "progressive" mask by specifying a non-nul distance
    threshold thr. In this case, if the distance between a pixel and the given
    color is d, the transparency will be 

    d**s / (thr**s + d**s)
    which is 1 when d>>thr and 0 for d<<thr, the stiffness of the effect being
    parametrized by s
    """
    if color is None:
        color = [0,0,0]

    # code a little sloppy, it just works.
    hill = lambda x: (1.0*(x!=0) if (thr==0) else (x**s/ (thr**s+x**s)))
    color = np.array(color)
    flim = lambda im: hill(np.sqrt(((im-color)**2).sum(axis=2)))
    mask = clip.fl_image(flim)
    mask.ismask= True
    newclip = clip.set_mask(mask)
    return newclip