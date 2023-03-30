import numpy as np


def fadein(clip, duration, initial_color=None):
    """Makes the clip progressively appear from some color (black by default),
    over ``duration`` seconds at the beginning of the clip. Can be used for
    masks too, where the initial color must be a number between 0 and 1.

    For cross-fading (progressive appearance or disappearance of a clip
    over another clip, see ``transfx.crossfadein``
    """
    if initial_color is None:
        initial_color = 0 if clip.is_mask else [0, 0, 0]

    initial_color = np.array(initial_color)

    def filter(get_frame, t):
        if t >= duration:
            return get_frame(t)
        else:
            fading = 1.0 * t / duration
            return fading * get_frame(t) + (1 - fading) * initial_color

    return clip.transform(filter)
