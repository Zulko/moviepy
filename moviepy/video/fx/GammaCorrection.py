from moviepy.Clip import Clip
from moviepy.Effect import Effect
from dataclasses import dataclass


@dataclass
class GammaCorrection(Effect):
    """Gamma-correction of a video clip."""

    gamma: float

    def apply(self, clip: Clip) -> Clip:
        def filter(im):
            corrected = 255 * (1.0 * im / 255) ** self.gamma
            return corrected.astype("uint8")

        return clip.image_transform(filter)
