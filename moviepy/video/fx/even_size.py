from moviepy.decorators import apply_to_mask


@apply_to_mask
def even_size(clip):
    """ 
    Crops the clip to make dimensions even.
    """
    w, h = clip.size
    w_even = w % 2 == 0
    h_even = h % 2 == 0
    if w_even and h_even:
        return clip
    
    if not w_even and not h_even:
        fl_image = lambda a : a[:-1,:-1,:]
    elif w_even:
        fl_image = lambda a : a[:,:-1,:]
    else:
        fl_image = lambda a : a[:-1,:,:]

    return clip.fl_image(fl_image)
