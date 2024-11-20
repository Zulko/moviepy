from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.Crop import Crop

from moviepy.Clip import Clip
from moviepy.Effect import Effect
from dataclasses import dataclass


@dataclass
class FreezeRegion(Effect):
    """Freezes one region of the clip while the rest remains animated.

    You can choose one of three methods by providing either `region`,
    `outside_region`, or `mask`.

    Parameters
    ----------

    t
      Time at which to freeze the freezed region.

    region
      A tuple (x1, y1, x2, y2) defining the region of the screen (in pixels)
      which will be freezed. You can provide outside_region or mask instead.

    outside_region
      A tuple (x1, y1, x2, y2) defining the region of the screen (in pixels)
      which will be the only non-freezed region.

    mask
      If not None, will overlay a freezed version of the clip on the current clip,
      with the provided mask. In other words, the "visible" pixels in the mask
      indicate the freezed region in the final picture.

    """

    t: float = 0
    region: tuple = None
    outside_region: tuple = None
    mask: Clip = None

    def apply(self, clip: Clip) -> Clip:
        if self.region is not None:
            x1, y1, x2, y2 = self.region
            freeze = (
                clip.with_effects([Crop(*self.region)])
                .to_ImageClip(t=self.t)
                .with_duration(clip.duration)
                .with_position((x1, y1))
            )
            return CompositeVideoClip([clip, freeze])

        elif self.outside_region is not None:
            x1, y1, x2, y2 = self.outside_region
            animated_region = clip.with_effects(
                [Crop(*self.outside_region)]
            ).with_position((x1, y1))
            freeze = clip.to_ImageClip(t=self.t).with_duration(clip.duration)
            return CompositeVideoClip([freeze, animated_region])

        elif self.mask is not None:
            freeze = (
                clip.to_ImageClip(t=t).with_duration(clip.duration).with_mask(self.mask)
            )
            return CompositeVideoClip([clip, freeze])
