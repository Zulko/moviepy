from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect
from moviepy.video.tools import cupy_utils


@dataclass
class LumContrast(Effect):
    """Luminosity-contrast correction of a clip."""

    lum: float = 0
    contrast: float = 0
    contrast_threshold: float = 127

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""

        def image_filter(im):
            if cupy_utils.is_cuda_array(im):
                cp = cupy_utils.cupy()
                im_f = im.astype(cp.float64)
                corrected = im_f + self.lum + self.contrast * (
                    im_f - float(self.contrast_threshold)
                )
                cp.clip(corrected, 0, 255, out=corrected)
                return corrected.astype(cp.uint8)

            im = 1.0 * im  # float conversion
            corrected = (
                im + self.lum + self.contrast * (im - float(self.contrast_threshold))
            )
            corrected[corrected < 0] = 0
            corrected[corrected > 255] = 255
            return corrected.astype("uint8")

        return clip.image_transform(image_filter)
