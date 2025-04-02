from dataclasses import dataclass

from moviepy.Effect import Effect


@dataclass
class Blink(Effect):
    """
    使剪辑闪烁。在每次闪烁时，它将显示 ``duration_on`` 秒，然后消失 ``duration_off`` 秒。
    仅在合成剪辑中有效。
    """

    duration_on: float
    duration_off: float

    def apply(self, clip):
        """Apply the effect to the clip."""
        if clip.mask is None:
            clip = clip.with_mask()

        duration = self.duration_on + self.duration_off
        clip.mask = clip.mask.transform(
            lambda get_frame, t: get_frame(t) * ((t % duration) < self.duration_on)
        )

        return clip
