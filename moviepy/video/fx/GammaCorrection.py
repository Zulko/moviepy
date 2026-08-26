from dataclasses import dataclass

import numpy as np

from moviepy.Clip import Clip
from moviepy.Effect import Effect
from moviepy.video.tools import cupy_utils


@dataclass
class GammaCorrection(Effect):
    """Gamma-correction of a video clip."""

    gamma: float

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""

        # Fast path: precompute a uint8 lookup table for uint8 frames.
        # Must match: (255 * (1.0 * im / 255) ** gamma).astype(uint8)
        # for positive values (i.e. truncation toward 0).
        lut_np = (
            255
            * (np.arange(256, dtype=np.float64) / 255.0) ** self.gamma
        ).astype(np.uint8)
        lut_cp = None

        def filter(im):
            nonlocal lut_cp

            if cupy_utils.is_cuda_array(im):
                cp = cupy_utils.cupy()
                if im.dtype == cp.uint8:
                    if lut_cp is None:
                        lut_cp = cp.asarray(lut_np)
                    return lut_cp[im]

                corrected = 255 * (im.astype(cp.float64) / 255.0) ** self.gamma
                return corrected.astype(cp.uint8)

            if isinstance(im, np.ndarray) and im.dtype == np.uint8:
                return lut_np[im]

            corrected = 255 * (1.0 * im / 255) ** self.gamma
            return corrected.astype("uint8")

        return clip.image_transform(filter)
