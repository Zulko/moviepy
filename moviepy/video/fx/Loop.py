from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class Loop(Effect):
    """
    Returns a clip that plays the current clip in an infinite loop.
    Ideal for clips coming from GIFs.

    Parameters
    ----------

    n
      Number of times the clip should be played. If `None` the
      the clip will loop indefinitely (i.e. with no set duration).

    duration
      Total duration of the clip. Can be specified instead of n.
    """

    n: int = None
    duration: float = None

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        if clip.duration is None:
            raise ValueError("Attribute 'duration' not set")

        previous_duration = clip.duration
        clip = clip.time_transform(
            lambda t: t % previous_duration, apply_to=["mask", "audio"]
        )

        if self.n:
            self.duration = self.n * previous_duration

        if self.duration:
            clip = clip.with_duration(self.duration)

        return clip
