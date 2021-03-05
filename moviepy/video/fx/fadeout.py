import numpy as np

from moviepy.decorators import requires_duration


@requires_duration
def fadeout(clip, duration, final_color=None):
    """Makes the clip progressively fade to some color (black by default),
    over ``duration`` seconds at the end of the clip. Can be used for masks too,
    where the final color must be a number between 0 and 1.

    For cross-fading (progressive appearance or disappearance of a clip over another
    clip, see ``transfx.crossfadeout``
    """
    if final_color is None:
        final_color = 0 if clip.is_mask else [0, 0, 0]

    final_color = np.array(final_color)

    def filter(get_frame, t):
        if (clip.duration - t) >= duration:
            return get_frame(t)
        else:
            fading = 1.0 * (clip.duration - t) / duration
            return fading * get_frame(t) + (1 - fading) * final_color

    return clip.transform(filter)
