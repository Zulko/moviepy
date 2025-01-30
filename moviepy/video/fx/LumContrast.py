from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class LumContrast(Effect):
    """Luminosity-contrast correction of a clip."""

    lum: float = 0
    contrast: float = 0
    contrast_threshold: float = 127

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""

        def image_filter(im):
            im = 1.0 * im  # float conversion
            corrected = (
                im + self.lum + self.contrast * (im - float(self.contrast_threshold))
            )
            corrected[corrected < 0] = 0
            corrected[corrected > 255] = 255
            return corrected.astype("uint8")

        return clip.image_transform(image_filter)
