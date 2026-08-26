from dataclasses import dataclass

import numpy as np

from moviepy.Clip import Clip
from moviepy.Effect import Effect
from moviepy.video.tools import cupy_utils


@dataclass
class FadeOut(Effect):
    """Makes the clip progressively fade to some color (black by default),
    over ``duration`` seconds at the end of the clip. Can be used for masks too,
    where the final color must be a number between 0 and 1.

    For cross-fading (progressive appearance or disappearance of a clip over another
    clip), see ``CrossFadeOut``
    """

    duration: float
    final_color: list = None

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        if clip.duration is None:
            raise ValueError("Attribute 'duration' not set")

        if self.final_color is None:
            self.final_color = 0 if clip.is_mask else [0, 0, 0]

        final_color = np.array(self.final_color)

        def filter(get_frame, t):
            if (clip.duration - t) >= self.duration:
                return get_frame(t)
            else:
                fading = 1.0 * (clip.duration - t) / self.duration
                frame = get_frame(t)
                if cupy_utils.is_cuda_array(frame):
                    cp = cupy_utils.cupy()
                    fin = final_color
                    if not cupy_utils.is_cuda_array(fin):
                        fin = cp.asarray(fin)
                    return fading * frame + (1 - fading) * fin
                return fading * frame + (1 - fading) * final_color

        return clip.transform(filter)
