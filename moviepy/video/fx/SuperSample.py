from dataclasses import dataclass

import numpy as np

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class SuperSample(Effect):
    """Replaces each frame at time t by the mean of `n_frames` equally spaced frames
    taken in the interval [t-d, t+d]. This results in motion blur.
    """

    d: float
    n_frames: int

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""

        def filter(get_frame, t):
            timings = np.linspace(t - self.d, t + self.d, self.n_frames)
            frame_average = np.mean(
                1.0 * np.array([get_frame(t_) for t_ in timings], dtype="uint16"),
                axis=0,
            )
            return frame_average.astype("uint8")

        return clip.transform(filter)
