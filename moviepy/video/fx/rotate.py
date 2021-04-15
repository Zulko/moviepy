import math
import warnings

import numpy as np


try:
    import PIL

    PIL_rotate_kwargs_supported = {
        # [moviepy rotate argument name,
        #  PIL.rotate argument supported,
        #  minimum PIL version required]
        "fillcolor": ["bg_color", False, (5, 2, 0)],
        "center": ["center", False, (4, 0, 0)],
        "translate": ["translate", False, (4, 0, 0)],
    }

    if hasattr(PIL, "__version__"):
        # check support for PIL.rotate arguments
        PIL__version_info__ = tuple(int(n) for n in PIL.__version__ if n.isdigit())

        for PIL_rotate_kw_name, support_data in PIL_rotate_kwargs_supported.items():
            if PIL__version_info__ >= support_data[2]:
                PIL_rotate_kwargs_supported[PIL_rotate_kw_name][1] = True

    Image = PIL.Image

except ImportError:  # pragma: no cover
    Image = None


def rotate(
    clip,
    angle,
    unit="deg",
    resample="bicubic",
    expand=True,
    center=None,
    translate=None,
    bg_color=None,
):
    """
    Rotates the specified clip by ``angle`` degrees (or radians) anticlockwise
    If the angle is not a multiple of 90 (degrees) or ``center``, ``translate``,
    and ``bg_color`` are not ``None``, the package ``pillow`` must be installed,
    and there will be black borders. You can make them transparent with:

    >>> new_clip = clip.add_mask().rotate(72)

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
    if Image:
        try:
            resample = {
                "bilinear": Image.BILINEAR,
                "nearest": Image.NEAREST,
                "bicubic": Image.BICUBIC,
            }[resample]
        except KeyError:
            raise ValueError(
                "'resample' argument must be either 'bilinear', 'nearest' or 'bicubic'"
            )

    if hasattr(angle, "__call__"):
        get_angle = angle
    else:
        get_angle = lambda t: angle

    def filter(get_frame, t):
        angle = get_angle(t)
        im = get_frame(t)

        if unit == "rad":
            angle = math.degrees(angle)

        angle %= 360
        if not center and not translate and not bg_color:
            if (angle == 0) and expand:
                return im
            if (angle == 90) and expand:
                transpose = [1, 0] if len(im.shape) == 2 else [1, 0, 2]
                return np.transpose(im, axes=transpose)[::-1]
            elif (angle == 270) and expand:
                transpose = [1, 0] if len(im.shape) == 2 else [1, 0, 2]
                return np.transpose(im, axes=transpose)[:, ::-1]
            elif (angle == 180) and expand:
                return im[::-1, ::-1]

        if not Image:
            raise ValueError(
                'Without "Pillow" installed, only angles that are a multiple of 90'
                " without centering, translation and background color transformations"
                ' are supported, please install "Pillow" with `pip install pillow`'
            )

        # build PIL.rotate kwargs
        kwargs, _locals = ({}, locals())
        for PIL_rotate_kw_name, (
            kw_name,
            supported,
            min_version,
        ) in PIL_rotate_kwargs_supported.items():
            # get the value passed to rotate FX from `locals()` dictionary
            kw_value = _locals[kw_name]

            if supported:  # if argument supported by PIL version
                kwargs[PIL_rotate_kw_name] = kw_value
            else:
                if kw_value is not None:  # if not default value
                    warnings.warn(
                        f"rotate '{kw_name}' argument is not supported"
                        " by your Pillow version and is being ignored. Minimum"
                        " Pillow version required:"
                        f" v{'.'.join(str(n) for n in min_version)}",
                        UserWarning,
                    )

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
                    angle, expand=expand, resample=resample, **kwargs
                )
            )
            / a
        )

    return clip.transform(filter, apply_to=["mask"])
