from dataclasses import dataclass

import cv2
import numpy as np

from moviepy.Clip import Clip
from moviepy.Effect import Effect


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
            im = get_frame(t).copy()
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
            return np.array(res, dtype=np.uint8)

        return clip.transform(filter)
