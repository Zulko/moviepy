from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class TimeMirror(Effect):
    """
    Returns a clip that plays the current clip backwards.
    The clip must have its ``duration`` attribute set.
    The same effect is applied to the clip's audio and mask if any.
    """

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        if clip.duration is None:
            raise ValueError("Attribute 'duration' not set")

        return clip[::-1]
