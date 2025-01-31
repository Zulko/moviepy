from dataclasses import dataclass

import numpy as np

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class FadeIn(Effect):
    """Makes the clip progressively appear from some color (black by default),
    over ``duration`` seconds at the beginning of the clip. Can be used for
    masks too, where the initial color must be a number between 0 and 1.

    For cross-fading (progressive appearance or disappearance of a clip
    over another clip, see ``CrossFadeIn``
    """

    duration: float
    initial_color: list = None

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        if self.initial_color is None:
            self.initial_color = 0 if clip.is_mask else [0, 0, 0]

        self.initial_color = np.array(self.initial_color)

        def filter(get_frame, t):
            if t >= self.duration:
                return get_frame(t)
            else:
                fading = 1.0 * t / self.duration
                return fading * get_frame(t) + (1 - fading) * self.initial_color

        return clip.transform(filter)
