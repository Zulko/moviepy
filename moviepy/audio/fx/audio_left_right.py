import numpy as np


def audio_left_right(audioclip, left=1, right=1, merge=False):
    """
    NOT YET FINISHED

    For a stereo audioclip, this function enables to change the volume
    of the left and right channel separately (with the factors `left`
    and `right`)
    Makes a stereo audio clip in which the volume of left and right
    is controllable
    """
    funleft = (lambda t: left) if np.isscalar(left) else left
    funright = (lambda t: right) if np.isscalar(right) else right
