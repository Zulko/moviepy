from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class GammaCorrection(Effect):
    """Gamma-correction of a video clip."""

    gamma: float

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""

        def filter(im):
            corrected = 255 * (1.0 * im / 255) ** self.gamma
            return corrected.astype("uint8")

        return clip.image_transform(filter)
