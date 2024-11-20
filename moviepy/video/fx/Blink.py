from dataclasses import dataclass

from moviepy.Effect import Effect


@dataclass
class Blink(Effect):
    """
    Makes the clip blink. At each blink it will be displayed ``duration_on``
    seconds and disappear ``duration_off`` seconds. Will only work in
    composite clips.
    """

    duration_on: float
    duration_off: float

    def apply(self, clip):
        """Apply the effect to the clip."""
        if clip.mask is None:
            clip = clip.with_add_mask()

        duration = self.duration_on + self.duration_off
        clip.mask = clip.mask.transform(
            lambda get_frame, t: get_frame(t) * ((t % duration) < self.duration_on)
        )

        return clip
