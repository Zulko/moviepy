import numbers


def _get_cv2_resizer():
    try:
        import cv2
    except ImportError:
        return (None, ["OpenCV not found (install 'opencv-python')"])

    def resizer(pic, new_size):
        lx, ly = int(new_size[0]), int(new_size[1])
        if lx > pic.shape[1] or ly > pic.shape[0]:
            # For upsizing use linear for good quality & decent speed
            interpolation = cv2.INTER_LINEAR
        else:
            # For dowsizing use area to prevent aliasing
            interpolation = cv2.INTER_AREA
        return cv2.resize(+pic.astype("uint8"), (lx, ly), interpolation=interpolation)

    return (resizer, [])


def _get_PIL_resizer():
    try:
        from PIL import Image
    except ImportError:
        return (None, ["PIL not found (install 'Pillow')"])

    import numpy as np

    def resizer(pic, new_size):
        new_size = list(map(int, new_size))[::-1]
        # shape = pic.shape
        # if len(shape) == 3:
        #     newshape = (new_size[0], new_size[1], shape[2])
        # else:
        #     newshape = (new_size[0], new_size[1])

        pil_img = Image.fromarray(pic)
        resized_pil = pil_img.resize(new_size[::-1], Image.ANTIALIAS)
        # arr = np.fromstring(resized_pil.tostring(), dtype="uint8")
        # arr.reshape(newshape)
        return np.array(resized_pil)

    return (resizer, [])


def _get_scipy_resizer():
    try:
        from scipy.misc import imresize
    except ImportError:
        try:
            from scipy import __version__ as __scipy_version__
        except ImportError:
            return (None, ["Scipy not found (install 'scipy' or 'Pillow')"])

        scipy_version_info = tuple(
            int(num) for num in __scipy_version__.split(".") if num.isdigit()
        )

        # ``scipy.misc.imresize`` was removed in v1.3.0
        if scipy_version_info >= (1, 3, 0):
            return (
                None,
                [
                    "scipy.misc.imresize not found (was removed in scipy v1.3.0,"
                    f" you are using v{__scipy_version__}, install 'Pillow')"
                ],
            )

        # unknown reason
        return (None, "scipy.misc.imresize not found")

    def resizer(pic, new_size):
        return imresize(pic, map(int, new_size[::-1]))

    return (resizer, [])


def _get_resizer():
    """Tries to define a ``resizer`` function using next libraries, in the given
    order:

    - cv2
    - PIL
    - scipy

    Returns a dictionary with following attributes:

    - ``resizer``: Function used to resize images in ``resize`` FX function.
    - ``origin``: Library used to resize.
    - ``error_msgs``: If any of the libraries is available, shows the user why
      this feature is not available and how to fix it in several error messages
      which are formatted in the error displayed, if resizing is not possible.
    """
    error_messages = []

    resizer_getters = {
        "cv2": _get_cv2_resizer,
        "PIL": _get_PIL_resizer,
        "scipy": _get_scipy_resizer,
    }
    for origin, resizer_getter in resizer_getters.items():
        resizer, _error_messages = resizer_getter()
        if resizer is not None:
            return {"resizer": resizer, "origin": origin, "error_msgs": []}
        else:
            error_messages.extend(_error_messages)

    return {"resizer": None, "origin": None, "error_msgs": reversed(error_messages)}


resizer = None
_resizer_data = _get_resizer()
if _resizer_data["resizer"] is not None:
    resizer = _resizer_data["resizer"]
    resizer.origin = _resizer_data["origin"]
    del _resizer_data["error_msgs"]


def resize(clip, new_size=None, height=None, width=None, apply_to_mask=True):
    """Returns a video clip that is a resized version of the clip.

    Parameters
    ----------

    new_size : tuple or float or function, optional
      Can be either
        - ``(width, height)`` in pixels or a float representing
        - A scaling factor, like ``0.5``.
        - A function of time returning one of these.

    width : int, optional
      Width of the new clip in pixels. The height is then computed so
      that the width/height ratio is conserved.

    height : int, optional
      Height of the new clip in pixels. The width is then computed so
      that the width/height ratio is conserved.

    Examples
    --------

    >>> myClip.resize( (460,720) ) # New resolution: (460,720)
    >>> myClip.resize(0.6) # width and height multiplied by 0.6
    >>> myClip.resize(width=800) # height computed automatically.
    >>> myClip.resize(lambda t : 1+0.02*t) # slow swelling of the clip
    """
    w, h = clip.size

    if new_size is not None:

        def translate_new_size(new_size_):
            """Returns a [w, h] pair from `new_size_`. If `new_size_` is a
            scalar, then work out the correct pair using the clip's size.
            Otherwise just return `new_size_`
            """
            if isinstance(new_size_, numbers.Number):
                return [new_size_ * w, new_size_ * h]
            else:
                return new_size_

        if hasattr(new_size, "__call__"):
            # The resizing is a function of time

            def get_new_size(t):
                return translate_new_size(new_size(t))

            if clip.is_mask:

                def filter(get_frame, t):
                    return (
                        resizer((255 * get_frame(t)).astype("uint8"), get_new_size(t))
                        / 255.0
                    )

            else:

                def filter(get_frame, t):
                    return resizer(get_frame(t).astype("uint8"), get_new_size(t))

            newclip = clip.transform(
                filter, keep_duration=True, apply_to=(["mask"] if apply_to_mask else [])
            )
            if apply_to_mask and clip.mask is not None:
                newclip.mask = resize(clip.mask, new_size, apply_to_mask=False)

            return newclip

        else:
            new_size = translate_new_size(new_size)

    elif height is not None:

        if hasattr(height, "__call__"):

            def func(t):
                return 1.0 * int(height(t)) / h

            return resize(clip, func)

        else:
            new_size = [w * height / h, height]

    elif width is not None:

        if hasattr(width, "__call__"):

            def func(t):
                return 1.0 * width(t) / w

            return resize(clip, func)

        else:
            new_size = [width, h * width / w]
    else:
        raise ValueError("You must provide either 'new_size' or 'height' or 'width'")

    # From here, the resizing is constant (not a function of time), size=newsize

    if clip.is_mask:

        def image_filter(pic):
            return 1.0 * resizer((255 * pic).astype("uint8"), new_size) / 255.0

    else:

        def image_filter(pic):
            return resizer(pic.astype("uint8"), new_size)

    new_clip = clip.image_transform(image_filter)

    if apply_to_mask and clip.mask is not None:
        new_clip.mask = resize(clip.mask, new_size, apply_to_mask=False)

    return new_clip


if resizer is None:
    del resizer

    doc = resize.__doc__

    def resize(clip, new_size=None, height=None, width=None):
        """Fallback resize FX function, if OpenCV, Scipy and PIL are not installed.

        This docstring will be replaced at runtime.
        """
        fix_tips = "- " + "\n- ".join(_resizer_data["error_msgs"])
        raise ImportError(f"fx resize needs OpenCV or Scipy or PIL\n{fix_tips}")

    resize.__doc__ = doc

del _resizer_data["origin"], _resizer_data["resizer"]
