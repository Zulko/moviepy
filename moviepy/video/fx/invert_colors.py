def invert_colors(clip):
    """ Returns the color-inversed clip.

    The values of all pixels are replaced with (255-v) or (1-v) for masks 
    Black becomes white, green becomes purple, etc.
    """
    maxi = 1.0 if clip.is_mask else 255
    return clip.with_image_filter(lambda f: maxi - f)
