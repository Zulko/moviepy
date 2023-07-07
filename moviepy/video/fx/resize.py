import numbers
from PIL import Image
import numpy as np


def resizer(pic, new_size):
        new_size = list(map(int, new_size))[::-1]

        pil_img = Image.fromarray(pic)
        resized_pil = pil_img.resize(new_size[::-1], Image.LANCZOS)
        return np.array(resized_pil)


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
