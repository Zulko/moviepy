from dataclasses import dataclass

import numpy as np

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class MultiplyColor(Effect):
    """
    Multiplies the clip's colors by the given factor, can be used
    to decrease or increase the clip's brightness (is that the
    right word ?)
    """

    factor: float

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        return clip.image_transform(
            lambda frame: np.minimum(255, (self.factor * frame)).astype("uint8")
        )
