from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips


@dataclass
class Freeze(Effect):
    """Momentarily freeze the clip at time t.

    Set `t='end'` to freeze the clip at the end (actually it will freeze on the
    frame at time clip.duration - padding_end seconds - 1 / clip_fps).
    With ``duration`` you can specify the duration of the freeze.
    With ``total_duration`` you can specify the total duration of
    the clip and the freeze (i.e. the duration of the freeze is
    automatically computed). One of them must be provided.
    """

    t: float = 0
    freeze_duration: float = None
    total_duration: float = None
    padding_end: float = 0

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
        return concatenate_videoclips(before + freeze + after)
