from dataclasses import dataclass

import cv2
import numpy as np

from moviepy.Clip import Clip
from moviepy.Effect import Effect
from moviepy.video.tools import cupy_utils


@dataclass
class HeadBlur(Effect):
    """Returns a filter that will blur a moving part (a head ?) of the frames.

    The position of the blur at time t is defined by (fx(t), fy(t)), the radius
    of the blurring by ``radius`` and the intensity of the blurring by ``intensity``.
    """

    fx: callable
    fy: callable
    radius: float
    intensity: float = None

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        if self.intensity is None:
            self.intensity = int(2 * self.radius / 3)

        def filter(get_frame, t):
            im = get_frame(t)
            is_cuda = cupy_utils.is_cuda_array(im)
            cp = cupy_utils.cupy() if is_cuda else None

            # Best-effort GPU-native path.
            if is_cuda:
                try:
                    from cupyx.scipy.ndimage import (  # type: ignore
                        gaussian_filter as _gaussian_filter,
                    )

                    im_cp = im
                    if im_cp.dtype != cp.uint8:
                        # Keep behavior close to the CPU path which always
                        # returns uint8.
                        im_cp = cp.clip(im_cp, 0, 255).astype(
                            cp.uint8
                        )

                    im_f = im_cp.astype(cp.float32)
                    h, w = int(im_f.shape[0]), int(im_f.shape[1])
                    x, y = int(self.fx(t)), int(self.fy(t))
                    r = float(self.radius)

                    # Approximate OpenCV's sigmaX=0 behavior.
                    k = int(self.intensity * 6)
                    k = (k + 1) if (k % 2 == 0) else k
                    sigma = 0.3 * (((k - 1) * 0.5) - 1.0) + 0.8
                    sigma = float(max(0.01, sigma))

                    # Build circular mask on GPU.
                    yy, xx = cp.ogrid[:h, :w]
                    mask = (xx - x) * (xx - x) + (yy - y) * (yy - y) <= (r * r)

                    blurred = _gaussian_filter(
                        im_f, sigma=(sigma, sigma, 0.0), mode="nearest"
                    )
                    out = cp.where(mask[:, :, None], blurred, im_f)
                    return cp.clip(out + 0.5, 0.0, 255.0).astype(cp.uint8)
                except Exception:
                    pass

                # Fallback: CPU OpenCV.
                im = cp.asnumpy(im)

            im = im.copy()
            h, w, d = im.shape
            x, y = int(self.fx(t)), int(self.fy(t))
            # Create a mask for the blur area
            blur_mask = np.zeros((h, w), dtype=np.uint8)
            cv2.circle(blur_mask, (x, y), int(self.radius), 255, -1)

            # Blur the image, size of the kernel must be odd
            gaussian_kernel = int(
                self.intensity * 6
            )  # 6 is a factor somewhat match the intensity of previous versions
            gaussian_kernel = (
                gaussian_kernel + 1 if gaussian_kernel % 2 == 0 else gaussian_kernel
            )

            blurred_im = cv2.GaussianBlur(
                im, (gaussian_kernel, gaussian_kernel), sigmaX=0
            )
            blur_mask = cv2.cvtColor(blur_mask, cv2.COLOR_GRAY2BGR)

            res = np.where(blur_mask == 255, blurred_im, im)
            res = np.array(res, dtype=np.uint8)
            return cp.asarray(res) if is_cuda else res

        return clip.transform(filter)
