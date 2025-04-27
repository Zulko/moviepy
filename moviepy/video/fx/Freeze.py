from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips


@dataclass
class Freeze(Effect):
    """在时间t暂时冻结剪辑。

    设置`t ='end'`以在结尾冻结剪辑（实际上它将在时间 clip.duration - padding_end seconds - 1 / clip_fps处的帧）。
    使用``duration``，您可以指定冻结的持续时间。
    使用``total_duration``，您可以指定剪辑和冻结（即，冻结的持续时间是自动计算）。其中一个必须提供。

    使用“update_start_end”，您可以定义效果是否必须保留和/或更新原始剪辑的开始和结束属性
    """

    t: float = 0
    freeze_duration: float = None
    total_duration: float = None
    padding_end: float = 0
    update_start_end: bool = True

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        if clip.duration is None:
            raise ValueError("Attribute 'duration' not set")

        if self.t == "end":
            self.t = clip.duration - self.padding_end - 1 / clip.fps

        if self.freeze_duration is None:
            if self.total_duration is None:
                raise ValueError(
                    "You must provide either 'freeze_duration' or 'total_duration'"
                )
            self.freeze_duration = self.total_duration - clip.duration

        before = [clip[: self.t]] if (self.t != 0) else []
        freeze = [clip.to_ImageClip(self.t).with_duration(self.freeze_duration)]
        after = [clip[self.t :]] if (self.t != clip.duration) else []

        new_clip = concatenate_videoclips(before + freeze + after)
        if self.update_start_end:
            if clip.start is not None:
                new_clip = new_clip.with_start(clip.start)
            if clip.end is not None:
                new_clip = new_clip.with_end(clip.end + self.freeze_duration)

        return new_clip
