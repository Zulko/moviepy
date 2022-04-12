import numpy as np


def mask_color(clip, color=None, threshold=0, stiffness=1):
    """Returns a new clip with a mask for transparency where the original
    clip is of the given color.

    You can also have a "progressive" mask by specifying a non-null distance
    threshold ``threshold``. In this case, if the distance between a pixel and
    the given color is d, the transparency will be

    d**stiffness / (threshold**stiffness + d**stiffness)

    which is 1 when d>>threshold and 0 for d<<threshold, the stiffness of the
    effect being parametrized by ``stiffness``
    """
    if color is None:
        color = [0, 0, 0]

    color = np.array(color)

    def hill(x):
        if threshold:
            return x**stiffness / (threshold**stiffness + x**stiffness)
        else:
            return 1.0 * (x != 0)

    def flim(im):
        return hill(np.sqrt(((im - color) ** 2).sum(axis=2)))

    mask = clip.image_transform(flim)
    mask.is_mask = True
    new_clip = clip.with_mask(mask)
    return new_clip
