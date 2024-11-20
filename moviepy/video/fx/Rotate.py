import math
from dataclasses import dataclass

import numpy as np
from PIL import Image

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class Rotate(Effect):
    """
    Rotates the specified clip by ``angle`` degrees (or radians) anticlockwise
    If the angle is not a multiple of 90 (degrees) or ``center``, ``translate``,
    and ``bg_color`` are not ``None``, there will be black borders.
    You can make them transparent with:

    >>> new_clip = clip.with_add_mask().rotate(72)

    Parameters
    ----------

    clip : VideoClip
    A video clip.

    angle : float
    Either a value or a function angle(t) representing the angle of rotation.

    unit : str, optional
    Unit of parameter `angle` (either "deg" for degrees or "rad" for radians).

    resample : str, optional
    An optional resampling filter. One of "nearest", "bilinear", or "bicubic".

    expand : bool, optional
    If true, expands the output image to make it large enough to hold the
    entire rotated image. If false or omitted, make the output image the same
    size as the input image.

    translate : tuple, optional
    An optional post-rotate translation (a 2-tuple).

    center : tuple, optional
    Optional center of rotation (a 2-tuple). Origin is the upper left corner.

    bg_color : tuple, optional
    An optional color for area outside the rotated image. Only has effect if
    ``expand`` is true.
    """

    angle: float
    unit: str = "deg"
    resample: str = "bicubic"
    expand: bool = True
    center: tuple = None
    translate: tuple = None
    bg_color: tuple = None

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        try:
            resample = {
                "bilinear": Image.BILINEAR,
                "nearest": Image.NEAREST,
                "bicubic": Image.BICUBIC,
            }[self.resample]
        except KeyError:
            raise ValueError(
                "'resample' argument must be either 'bilinear', 'nearest' or 'bicubic'"
            )

        if hasattr(self.angle, "__call__"):
            get_angle = self.angle
        else:
            get_angle = lambda t: self.angle

        def filter(get_frame, t):
            angle = get_angle(t)
            im = get_frame(t)

            if self.unit == "rad":
                angle = math.degrees(angle)

            angle %= 360
            if not self.center and not self.translate and not self.bg_color:
                if (angle == 0) and self.expand:
                    return im
                if (angle == 90) and self.expand:
                    transpose = [1, 0] if len(im.shape) == 2 else [1, 0, 2]
                    return np.transpose(im, axes=transpose)[::-1]
                elif (angle == 270) and self.expand:
                    transpose = [1, 0] if len(im.shape) == 2 else [1, 0, 2]
                    return np.transpose(im, axes=transpose)[:, ::-1]
                elif (angle == 180) and self.expand:
                    return im[::-1, ::-1]

            pillow_kwargs = {}

            if self.bg_color is not None:
                pillow_kwargs["fillcolor"] = self.bg_color

            if self.center is not None:
                pillow_kwargs["center"] = self.center

            if self.translate is not None:
                pillow_kwargs["translate"] = self.translate

            # PIL expects uint8 type data. However a mask image has values in the
            # range [0, 1] and is of float type.  To handle this we scale it up by
            # a factor 'a' for use with PIL and then back again by 'a' afterwards.
            if im.dtype == "float64":
                # this is a mask image
                a = 255.0
            else:
                a = 1

            # call PIL.rotate
            return (
                np.array(
                    Image.fromarray(np.array(a * im).astype(np.uint8)).rotate(
                        angle, expand=self.expand, resample=resample, **pillow_kwargs
                    )
                )
                / a
            )

        return clip.transform(filter, apply_to=["mask"])
