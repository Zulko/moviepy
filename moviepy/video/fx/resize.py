resize_possible = True

try:
    # TRY USING OpenCV AS RESIZER
    # raise ImportError #debugging
    import cv2
    import numpy as np

    def resizer(pic, new_size):
        lx, ly = int(new_size[0]), int(new_size[1])
        if lx > pic.shape[1] or ly > pic.shape[0]:
            # For upsizing use linear for good quality & decent speed
            interpolation = cv2.INTER_LINEAR
        else:
            # For dowsizing use area to prevent aliasing
            interpolation = cv2.INTER_AREA
        return cv2.resize(+pic.astype("uint8"), (lx, ly), interpolation=interpolation)

    resizer.origin = "cv2"

except ImportError:

    try:
        # TRY USING PIL/PILLOW AS RESIZER
        from PIL import Image
        import numpy as np

        def resizer(pic, new_size):
            new_size = list(map(int, new_size))[::-1]
            shape = pic.shape
            if len(shape) == 3:
                newshape = (new_size[0], new_size[1], shape[2])
            else:
                newshape = (new_size[0], new_size[1])

            pil_img = Image.fromarray(pic)
            resized_pil = pil_img.resize(new_size[::-1], Image.ANTIALIAS)
            # arr = np.fromstring(resized_pil.tostring(), dtype='uint8')
            # arr.reshape(newshape)
            return np.array(resized_pil)

        resizer.origin = "PIL"

    except ImportError:
        # TRY USING SCIPY AS RESIZER
        try:
            from scipy.misc import imresize

            def resizer(pic, new_size):
                return imresize(pic, map(int, new_size[::-1]))

            resizer.origin = "Scipy"

        except ImportError:
            resize_possible = False


def resize(clip, new_size=None, height=None, width=None, apply_to_mask=True):
    """
    Returns a video clip that is a resized version of the clip.

    Parameters
    ------------

    new_size:
      Can be either
        - ``(width,height)`` in pixels or a float representing
        - A scaling factor, like 0.5
        - A function of time returning one of these.

    width:
      width of the new clip in pixel. The height is then computed so
      that the width/height ratio is conserved.

    height:
      height of the new clip in pixel. The width is then computed so
      that the width/height ratio is conserved.

    Examples
    ----------

    >>> myClip.resize( (460,720) ) # New resolution: (460,720)
    >>> myClip.resize(0.6) # width and heigth multiplied by 0.6
    >>> myClip.resize(width=800) # height computed automatically.
    >>> myClip.resize(lambda t : 1+0.02*t) # slow swelling of the clip

    """

    w, h = clip.size

    if new_size is not None:

        def translate_new_size(new_size_):
            """
            Returns a [w, h] pair from `new_size_`. If `new_size_` is a scalar, then work out
            the correct pair using the clip's size. Otherwise just return `new_size_`
            """
            if isinstance(new_size_, (int, float)):
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


if not resize_possible:
    doc = resize.__doc__

    def resize(clip, new_size=None, height=None, width=None):
        raise ImportError("fx resize needs OpenCV or Scipy or PIL")

    resize.__doc__ = doc
