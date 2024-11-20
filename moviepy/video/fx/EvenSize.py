from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class EvenSize(Effect):
    """Crops the clip to make dimensions even."""

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        w, h = clip.size
        w_even = w % 2 == 0
        h_even = h % 2 == 0
        if w_even and h_even:
            return clip

        if not w_even and not h_even:

            def image_filter(a):
                return a[:-1, :-1, :]

        elif h_even:

            def image_filter(a):
                return a[:, :-1, :]

        else:

            def image_filter(a):
                return a[:-1, :, :]

        return clip.image_transform(image_filter, apply_to=["mask"])
