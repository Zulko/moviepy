import numpy as np

from moviepy.video.VideoClip import ImageClip


def mask_and(clip, other_clip):
    """Returns the logical 'and' (minimum pixel color values) between two masks.

    The result has the duration of the clip to which has been applied, if it has any.

    Parameters
    ----------

    other_clip ImageClip or np.ndarray
      Clip used to mask the original clip.

    Examples
    --------

    >>> clip = ColorClip(color=(255, 0, 0), size=(1, 1))  # red
    >>> mask = ColorClip(color=(0, 255, 0), size=(1, 1))  # green
    >>> masked_clip = clip.fx(mask_and, mask)             # black
    >>> masked_clip.get_frame(0)
    [[[0 0 0]]]
    """
    # to ensure that 'and' of two ImageClips will be an ImageClip
    if isinstance(other_clip, ImageClip):
        other_clip = other_clip.img

    if isinstance(other_clip, np.ndarray):
        return clip.image_transform(lambda frame: np.minimum(frame, other_clip))
    else:
        return clip.transform(
            lambda get_frame, t: np.minimum(get_frame(t), other_clip.get_frame(t))
        )
