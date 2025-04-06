from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class MultiplySpeed(Effect):
    """
    返回以乘以“因子”的速度播放当前剪辑的剪辑。

    除了因子之外，还可以指示剪辑所需的“最终持续时间”，并且该因子将自动计算。 相同的效果将应用于剪辑的音频和掩码（如果有）。
    """

    factor: float = None
    final_duration: float = None

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        if self.final_duration:
            self.factor = 1.0 * clip.duration / self.final_duration

        new_clip = clip.time_transform(
            lambda t: self.factor * t, apply_to=["mask", "audio"]
        )

        if clip.duration is not None:
            new_clip = new_clip.with_duration(1.0 * clip.duration / self.factor)

        return new_clip
