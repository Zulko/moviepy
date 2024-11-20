from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect
from moviepy.video.fx.FadeIn import FadeIn


@dataclass
class CrossFadeIn(Effect):
    """Makes the clip appear progressively, over ``duration`` seconds.
    Only works when the clip is included in a CompositeVideoClip.
    """

    duration: float

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        if clip.duration is None:
            raise ValueError("Attribute 'duration' not set")

        if clip.mask is None:
            clip = clip.with_add_mask()

        clip.mask.duration = clip.duration
        clip.mask = clip.mask.with_effects([FadeIn(self.duration)])

        return clip
