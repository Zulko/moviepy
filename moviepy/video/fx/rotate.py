import numpy as np

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
    If the angle is not a multiple of 90 (degrees), the package ``pillow`` must
    be installed, and there will be black borders. You can make them
    transparent with

    >>> new_clip = clip.add_mask().rotate(72)

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
      Only applIf False, the clip will maintain the same True, the clip will be
      resized so that the whole
    """
    if PIL_FOUND:
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

    def filter(get_frame, t):

        angle = get_angle(t)
        im = get_frame(t)

        if unit == "rad":
            angle = 360.0 * angle / (2 * np.pi)

        transpose = [1, 0] if len(im.shape) == 2 else [1, 0, 2]

        angle %= 360
        if (angle == 0) and expand:
            return im
        if (angle == 90) and expand:
            return np.transpose(im, axes=transpose)[::-1]
        elif (angle == 270) and expand:
            return np.transpose(im, axes=transpose)[:, ::-1]
        elif (angle == 180) and expand:
            return im[::-1, ::-1]
        elif not PIL_FOUND:
            raise ValueError(
                'Without "Pillow" installed, only angles that are a multiple of 90'
                ' are supported, please install "Pillow" with `pip install pillow`'
            )
        else:
            return pil_rotater(im, angle, resample=resample, expand=expand)

    return clip.transform(filter, apply_to=["mask"])
