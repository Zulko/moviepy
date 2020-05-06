import numpy as np

from moviepy.decorators import apply_to_mask

try:
    from PIL import Image

    PIL_FOUND = True

    def pil_rotater(pic, angle, resample, expand):
        # Ensures that pic is of the correct type
        return np.array(
            Image.fromarray(np.array(pic).astype(np.uint8)).rotate(
                angle, expand=expand, resample=resample
            )
        )


except ImportError:
    PIL_FOUND = False


def rotate(clip, angle, unit="deg", resample="bicubic", expand=True):
    """
    Rotates the specified clip by ``angle`` degrees (or radians) anticlockwise
    If the angle is not a multiple of 90 (degrees), the package ``pillow`` must be installed,
    and there will be black borders. You can make them transparent with

    >>> newclip = clip.add_mask().rotate(72)

    Parameters
    ===========

    clip
      A video clip

    angle
      Either a value or a function angle(t) representing the angle of rotation

    unit
      Unit of parameter `angle` (either `deg` for degrees or `rad` for radians).
      Default: `deg`

    resample
      One of "nearest", "bilinear", or "bicubic".

    expand
      Only applIf False, the clip will maintain the same True, the clip will be resized so that the whole
    """
    if PIL_FOUND:
        resample = {
            "bilinear": Image.BILINEAR,
            "nearest": Image.NEAREST,
            "bicubic": Image.BICUBIC,
        }[resample]

    if not hasattr(angle, "__call__"):
        # if angle is a constant, convert to a constant function
        a = +angle

        def angle(t):
            return a

    transpo = [1, 0] if clip.ismask else [1, 0, 2]

    def fl(gf, t):

        a = angle(t)
        im = gf(t)

        if unit == "rad":
            a = 360.0 * a / (2 * np.pi)

        a %= 360
        if (a == 0) and expand:
            return im
        if (a == 90) and expand:
            return np.transpose(im, axes=transpo)[::-1]
        elif (a == 270) and expand:
            return np.transpose(im, axes=transpo)[:, ::-1]
        elif (a == 180) and expand:
            return im[::-1, ::-1]
        elif not PIL_FOUND:
            raise ValueError(
                'Without "Pillow" installed, only angles that are a multiple of 90'
                ' are supported, please install "Pillow" with `pip install pillow`'
            )
        else:
            return pil_rotater(im, a, resample=resample, expand=expand)

    return clip.fl(fl, apply_to=["mask"])
