import numpy as np


def multiply_color(clip, factor):
    """
    Multiplies the clip's colors by the given factor, can be used
    to decrease or increase the clip's brightness (is that the
    right word?)

    Parameters
    ----------
    clip : Clip
    factor : float, default True
        How much the clip's colors are multiplied by.

    """
    return clip.image_transform(
        lambda frame: np.minimum(255, (factor * frame)).astype("uint8")
    )
