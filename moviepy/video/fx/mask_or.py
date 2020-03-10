import numpy as np

from ..VideoClip import ImageClip


def mask_or(clip, other_clip):
    """ Returns the logical 'or' (max) between two masks.
        other_clip can be a mask clip or a picture (np.array).
        The result has the duration of 'clip' (if it has any)
    """

    # To ensure that 'or' of two ImageClips will be an ImageClip.
    if isinstance(other_clip, ImageClip):
    	other_clip = other_clip.img

    if isinstance(other_clip, np.ndarray):
    	return clip.fl_image(lambda f : np.maximum(f, other_clip))
    else:
    	return clip.fl(lambda gf, t : np.maximum(gf(t),
                                                 other_clip.get_frame(t)))
