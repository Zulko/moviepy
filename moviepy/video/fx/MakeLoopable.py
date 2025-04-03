from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.CrossFadeIn import CrossFadeIn


@dataclass
class MakeLoopable(Effect):
    """使剪辑在自己的结束逐渐淡入，这种方式可以无限循环

    Parameters
    ----------
    重叠持续时间：浮点数
        淡入持续时间（以秒为单位）。
    """

    overlap_duration: float

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        clip2 = clip.with_effects([CrossFadeIn(self.overlap_duration)]).with_start(
            clip.duration - self.overlap_duration
        )
        return CompositeVideoClip([clip, clip2]).subclipped(
            self.overlap_duration, clip.duration
        )
