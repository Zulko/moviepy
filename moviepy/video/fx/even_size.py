import numpy as np

from moviepy.decorators import apply_to_mask

@apply_to_mask
def even_size(clip):
    """ Crops the clip to make dimensions even.

    """

    w,h = clip.size

    if (w%2 == 0) and (h%2==0):
        return clip
    
    if (w%2 != 0) and (h%2!=0):
        def fl_image(a): return a[:-1,:-1,:]
    elif (w%2 != 0):
        def fl_image(a): return a[:,:-1,:]
    else:
        def fl_image(a): return a[:-1,:,:]

    return clip.fl_image(fl_image)


