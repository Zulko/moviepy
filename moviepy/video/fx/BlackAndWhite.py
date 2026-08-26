from dataclasses import dataclass

import numpy as np

from moviepy.Effect import Effect
from moviepy.video.tools import cupy_utils


@dataclass
class BlackAndWhite(Effect):
    """Desaturates the picture, makes it black and white.
    Parameter RGB allows to set weights for the different color
    channels.
    If RBG is 'CRT_phosphor' a special set of values is used.
    preserve_luminosity maintains the sum of RGB to 1.
    """

    RGB: str = None
    preserve_luminosity: bool = True

    def apply(self, clip):
        """Apply the effect to the clip."""
        if self.RGB is None:
            self.RGB = [1, 1, 1]

        if self.RGB == "CRT_phosphor":
            self.RGB = [0.2125, 0.7154, 0.0721]

        R, G, B = (
            1.0
            * np.array(self.RGB)
            / (sum(self.RGB) if self.preserve_luminosity else 1)
        )

        def filter(im):
            xp = np
            if cupy_utils.is_cuda_array(im):
                xp = cupy_utils.cupy()

            im = R * im[:, :, 0] + G * im[:, :, 1] + B * im[:, :, 2]
            return xp.dstack(3 * [im]).astype(xp.uint8)

        return clip.image_transform(filter)
