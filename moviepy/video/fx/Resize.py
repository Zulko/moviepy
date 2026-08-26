import numbers
from dataclasses import dataclass
from typing import Union

import cv2

from moviepy.Effect import Effect
from moviepy.video.tools import cupy_utils


@dataclass
class Resize(Effect):
    """Effect returning a video clip that is a resized version of the clip.

    Parameters
    ----------

    new_size : tuple or float or function, optional
        Can be either
        - ``(width, height)`` in pixels or a float representing
        - A scaling factor, like ``0.5``.
        - A function of time returning one of these.

    height : int, optional
        Height of the new clip in pixels. The width is then computed so
        that the width/height ratio is conserved.

    width : int, optional
        Width of the new clip in pixels. The height is then computed so
        that the width/height ratio is conserved.

    Examples
    --------

    .. code:: python

        clip.with_effects([vfx.Resize((460,720))]) # New resolution: (460,720)
        clip.with_effects([vfx.Resize(0.6)]) # width and height multiplied by 0.6
        clip.with_effects([vfx.Resize(width=800)]) # height computed automatically.
        clip.with_effects([vfx.Resize(lambda t : 1+0.02*t)]) # slow clip swelling
    """

    new_size: Union[tuple, float, callable] = None
    height: int = None
    width: int = None
    apply_to_mask: bool = True

    def resizer(self, pic, new_size):
        """Resize the image.

        If the input is a CUDA array, try a GPU-native CuPy/CuPyX path first
        (best-effort) to keep effect chains on the GPU.
        """
        if cupy_utils.is_cuda_array(pic):
            cp = cupy_utils.cupy()
            lx, ly = int(new_size[0]), int(new_size[1])

            # Best-effort GPU resize.
            try:
                from cupyx.scipy.ndimage import zoom as _zoom  # type: ignore

                h0, w0 = int(pic.shape[0]), int(pic.shape[1])
                if h0 <= 0 or w0 <= 0:
                    return pic

                zx = float(lx) / float(w0)
                zy = float(ly) / float(h0)
                if pic.ndim == 3:
                    factors = (zy, zx, 1.0)
                else:
                    factors = (zy, zx)

                # Use order=1 (bilinear) as a good default. This doesn't
                # perfectly match OpenCV's AREA downsampling, but keeps data
                # on-GPU and is generally high quality.
                src_dtype = pic.dtype
                work = pic.astype(cp.float32, copy=False)
                out = _zoom(
                    work,
                    factors,
                    order=1,
                    mode="nearest",
                    prefilter=False,
                )

                if src_dtype == cp.uint8:
                    out = cp.clip(out + 0.5, 0.0, 255.0).astype(cp.uint8)
                else:
                    out = out.astype(src_dtype, copy=False)

                return out
            except Exception:
                # Fall back to CPU OpenCV path.
                pic = cp.asnumpy(pic)
                cp_out = cp
            else:
                cp_out = cp
        else:
            cp_out = None

        lx, ly = int(new_size[0]), int(new_size[1])
        if lx > pic.shape[1] or ly > pic.shape[0]:
            # For upsizing use linear for good quality & decent speed
            interpolation = cv2.INTER_LINEAR
        else:
            # For dowsizing use area to prevent aliasing
            interpolation = cv2.INTER_AREA

        resized = cv2.resize(
            +pic.astype("uint8"),
            (lx, ly),
            interpolation=interpolation,
        )
        if cp_out is not None:
            return cp_out.asarray(resized)
        return resized

    def apply(self, clip):
        """Apply the effect to the clip."""
        w, h = clip.size

        if self.new_size is not None:

            def translate_new_size(new_size_):
                """Returns a [w, h] pair from `new_size_`. If `new_size_` is a
                scalar, then work out the correct pair using the clip's size.
                Otherwise just return `new_size_`
                """
                if isinstance(new_size_, numbers.Number):
                    return [new_size_ * w, new_size_ * h]
                else:
                    return new_size_

            if hasattr(self.new_size, "__call__"):
                # The resizing is a function of time

                def get_new_size(t):
                    return translate_new_size(self.new_size(t))

                if clip.is_mask:

                    def filter(get_frame, t):
                        return (
                            self.resizer(
                                (255 * get_frame(t)).astype("uint8"), get_new_size(t)
                            )
                            / 255.0
                        )

                else:

                    def filter(get_frame, t):
                        return self.resizer(
                            get_frame(t).astype("uint8"), get_new_size(t)
                        )

                newclip = clip.transform(
                    filter,
                    keep_duration=True,
                    apply_to=(["mask"] if self.apply_to_mask else []),
                )
                if self.apply_to_mask and clip.mask is not None:
                    newclip.mask = clip.mask.with_effects(
                        [Resize(self.new_size, apply_to_mask=False)]
                    )

                return newclip

            else:
                self.new_size = translate_new_size(self.new_size)

        elif self.height is not None:
            if hasattr(self.height, "__call__"):

                def func(t):
                    return 1.0 * int(self.height(t)) / h

                return clip.with_effects([Resize(func)])

            else:
                self.new_size = [w * self.height / h, self.height]

        elif self.width is not None:
            if hasattr(self.width, "__call__"):

                def func(t):
                    return 1.0 * self.width(t) / w

                return clip.with_effects([Resize(func)])

            else:
                self.new_size = [self.width, h * self.width / w]
        else:
            raise ValueError(
                "You must provide either 'new_size' or 'height' or 'width'"
            )

        # From here, the resizing is constant (not a function of time), size=newsize

        if clip.is_mask:

            def image_filter(pic):
                return (
                    1.0
                    * self.resizer((255 * pic).astype("uint8"), self.new_size)
                    / 255.0
                )

        else:

            def image_filter(pic):
                return self.resizer(pic.astype("uint8"), self.new_size)

        new_clip = clip.image_transform(image_filter)

        if self.apply_to_mask and clip.mask is not None:
            new_clip.mask = clip.mask.with_effects(
                [Resize(self.new_size, apply_to_mask=False)]
            )

        return new_clip
