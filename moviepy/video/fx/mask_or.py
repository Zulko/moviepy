import numpy as np

from moviepy.video.VideoClip import ImageClip


def mask_or(clip, other_clip):
    """Returns the logical 'or' (max) between two masks.
    other_clip can be a mask clip or a picture (np.array).
    The result has the duration of 'clip' (if it has any)
    """

    # To ensure that 'or' of two ImageClips will be an ImageClip.
    if isinstance(other_clip, ImageClip):
        other_clip = other_clip.img

    if isinstance(other_clip, np.ndarray):
        return clip.image_transform(lambda frame: np.maximum(frame, other_clip))
    else:
        return clip.transform(
            lambda get_frame, t: np.maximum(get_frame(t), other_clip.get_frame(t))
        )
