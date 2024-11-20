from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class TimeSymmetrize(Effect):
    """
    Returns a clip that plays the current clip once forwards and
    then once backwards. This is very practival to make video that
    loop well, e.g. to create animated GIFs.
    This effect is automatically applied to the clip's mask and audio
    if they exist.
    """

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        if clip.duration is None:
            raise ValueError("Attribute 'duration' not set")

        return clip + clip[::-1]
