import numpy as np

from moviepy.video.VideoClip import ImageClip


def mask_or(clip, other_clip):
    """Returns the logical 'or' (maximum pixel color values) between two masks.

    The result has the duration of the clip to which has been applied, if it has any.

    Parameters
    ----------

    other_clip ImageClip or np.ndarray
      Clip used to mask the original clip.

    Examples
    --------

    >>> clip = ColorClip(color=(255, 0, 0), size=(1, 1))  # red
    >>> mask = ColorClip(color=(0, 255, 0), size=(1, 1))  # green
    >>> masked_clip = clip.fx(mask_or, mask)              # yellow
    >>> masked_clip.get_frame(0)
    [[[255 255   0]]]
    """
    # to ensure that 'or' of two ImageClips will be an ImageClip
    if isinstance(other_clip, ImageClip):
        other_clip = other_clip.img

    if isinstance(other_clip, np.ndarray):
        return clip.image_transform(lambda frame: np.maximum(frame, other_clip))
    else:
        return clip.transform(
            lambda get_frame, t: np.maximum(get_frame(t), other_clip.get_frame(t))
        )
