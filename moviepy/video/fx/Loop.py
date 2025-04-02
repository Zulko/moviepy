from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class Loop(Effect):
    """
    返回一个无限循环播放当前剪辑的剪辑。
    适用于来自 GIF 的剪辑。

    参数
    ----------
    n
      剪辑应播放的次数。如果 `None`，则剪辑将无限循环（即，没有设置持续时间）。

    duration
      剪辑的总持续时间。可以代替 n 指定。
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
