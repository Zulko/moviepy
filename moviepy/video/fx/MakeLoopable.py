from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

from moviepy.Clip import Clip
from moviepy.Effect import Effect
from dataclasses import dataclass

@dataclass
class MakeLoopable(Effect) :
    """Makes the clip fade in progressively at its own end, this way it can be
    looped indefinitely.

    Parameters
    ----------

    overlap_duration : float
      Duration of the fade-in (in seconds).
    """

    overlap_duration: float

    def apply(self, clip: Clip) -> Clip:
    
        clip2 = clip.crossfadein(self.overlap_duration).with_start(
            clip.duration - self.overlap_duration
        )
        return CompositeVideoClip([clip, clip2]).with_subclip(self.overlap_duration, clip.duration)
