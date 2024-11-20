from dataclasses import dataclass
from typing import Union

import numpy as np

from moviepy.Clip import Clip
from moviepy.Effect import Effect
from moviepy.video.VideoClip import ImageClip


@dataclass
class MasksAnd(Effect):
    """Returns the logical 'and' (minimum pixel color values) between two masks.

    The result has the duration of the clip to which has been applied, if it has any.

    Parameters
    ----------

    other_clip ImageClip or np.ndarray
      Clip used to mask the original clip.

    Examples
    --------

    >>> clip = ColorClip(color=(255, 0, 0), size=(1, 1))      # red
    >>> mask = ColorClip(color=(0, 255, 0), size=(1, 1))      # green
    >>> masked_clip = clip.with_effects([vfx.MasksAnd(mask)]) # black
    >>> masked_clip.get_frame(0)
    [[[0 0 0]]]
    """

    other_clip: Union[Clip, np.ndarray]

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        # to ensure that 'and' of two ImageClips will be an ImageClip
        if isinstance(self.other_clip, ImageClip):
            self.other_clip = self.other_clip.img

        if isinstance(self.other_clip, np.ndarray):
            return clip.image_transform(
                lambda frame: np.minimum(frame, self.other_clip)
            )
        else:
            return clip.transform(
                lambda get_frame, t: np.minimum(
                    get_frame(t), self.other_clip.get_frame(t)
                )
            )
