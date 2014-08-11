def mask_inv(clip):
    """ Returns the color-inversed mask."""
    return clip.fl_image(lambda f : 1.0 - f)