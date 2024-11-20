from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class SlideIn(Effect):
    """Makes the clip arrive from one side of the screen.

    Only works when the clip is included in a CompositeVideoClip,
    and if the clip has the same size as the whole composition.

    Parameters
    ----------

    clip : moviepy.Clip.Clip
      A video clip.

    duration : float
      Time taken for the clip to be fully visible

    side : str
      Side of the screen where the clip comes from. One of
      'top', 'bottom', 'left' or 'right'.

    Examples
    --------

    >>> from moviepy import *
    >>>
    >>> clips = [... make a list of clips]
    >>> slided_clips = [
    ...     CompositeVideoClip([clip.with_effects([vfx.SlideIn(1, "left")])])
    ...     for clip in clips
    ... ]
    >>> final_clip = concatenate_videoclips(slided_clips, padding=-1)
    >>>
    >>> clip = ColorClip(
    ...     color=(255, 0, 0), duration=1, size=(300, 300)
    ... ).with_fps(60)
    >>> final_clip = CompositeVideoClip([clip.with_effects([vfx.SlideIn(1, "right")])])
    """

    duration: float
    side: str

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        w, h = clip.size
        pos_dict = {
            "left": lambda t: (min(0, w * (t / self.duration - 1)), "center"),
            "right": lambda t: (max(0, w * (1 - t / self.duration)), "center"),
            "top": lambda t: ("center", min(0, h * (t / self.duration - 1))),
            "bottom": lambda t: ("center", max(0, h * (1 - t / self.duration))),
        }

        return clip.with_position(pos_dict[self.side])
