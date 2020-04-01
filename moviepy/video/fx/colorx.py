import numpy as np


def colorx(clip, factor):
    """
    Multiplies the clip's colors by the given factor, can be used
    to decrease or increase the clip's brightness (is that the
    right word ?)
    """
    return clip.fl_image(lambda pic: np.minimum(255, (factor * pic)).astype("uint8"))
