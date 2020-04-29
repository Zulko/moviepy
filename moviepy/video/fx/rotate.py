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
    Change unit to 'rad' to define angles as radians.
    If the angle is not one of 90, 180, -90, -180 (degrees) there will be
    black borders. You can make them transparent with

    >>> new_clip = clip.add_mask().rotate(72)

    Parameters
    ===========

    clip
      A video clip

    angle
      Either a value or a function angle(t) representing the angle of rotation

    unit
      Unit of parameter `angle` (either `deg` for degrees or `rad` for radians)

    resample
      One of "nearest", "bilinear", or "bicubic".

    expand
      Only applIf False, the clip will maintain the same True, the clip will be resized so that the whole
    """

    resample = {
        "bilinear": Image.BILINEAR,
        "nearest": Image.NEAREST,
        "bicubic": Image.BICUBIC,
    }[resample]

    if hasattr(angle, "__call__"):
        # angle is a function
        get_angle = angle
    else:
        # angle is a constant so convert to a constant function
        def get_angle(t):
            return angle

    transpose = [1, 0] if clip.is_mask else [1, 0, 2]

    def filter(get_frame, t):

        angle = get_angle(t)
        im = get_frame(t)

        if unit == "rad":
            angle = 360.0 * angle / (2 * np.pi)

        if (angle == 90) and expand:
            return np.transpose(im, axes=transpose)[::-1]
        elif (angle == -90) and expand:
            return np.transpose(im, axes=transpose)[:, ::-1]
        elif (angle in [180, -180]) and expand:
            return im[::-1, ::-1]
        elif not PIL_FOUND:
            raise ValueError(
                'Without "Pillow" installed, only angles 90, -90,'
                '180 are supported, please install "Pillow" with'
                "pip install pillow"
            )
        else:
            return pil_rotater(im, angle, resample=resample, expand=expand)

    return clip.with_filter(filter, apply_to=["mask"])
