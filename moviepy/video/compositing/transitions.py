"""Here is the current catalogue. These are meant to be used with ``clip.fx``
There are available as ``transfx.crossfadein`` etc.
"""

from moviepy.decorators import add_mask_if_none, requires_duration
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout


__all__ = ["crossfadein", "crossfadeout", "slide_in", "slide_out"]


@requires_duration
@add_mask_if_none
def crossfadein(clip, duration):
    """Makes the clip appear progressively, over ``duration`` seconds.
    Only works when the clip is included in a CompositeVideoClip.
    """
    clip.mask.duration = clip.duration
    new_clip = clip.copy()
    new_clip.mask = clip.mask.fx(fadein, duration)
    return new_clip


@requires_duration
@add_mask_if_none
def crossfadeout(clip, duration):
    """Makes the clip disappear progressively, over ``duration`` seconds.
    Only works when the clip is included in a CompositeVideoClip.
    """
    clip.mask.duration = clip.duration
    new_clip = clip.copy()
    new_clip.mask = clip.mask.fx(fadeout, duration)
    return new_clip


def slide_in(clip, duration, side):
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
    ...     CompositeVideoClip([clip.fx(transfx.slide_in, 1, "left")])
    ...     for clip in clips
    ... ]
    >>> final_clip = concatenate_videoclips(slided_clips, padding=-1)
    >>>
    >>> clip = ColorClip(
    ...     color=(255, 0, 0), duration=1, size=(300, 300)
    ... ).with_fps(60)
    >>> final_clip = CompositeVideoClip([transfx.slide_in(clip, 1, "right")])
    """
    w, h = clip.size
    pos_dict = {
        "left": lambda t: (min(0, w * (t / duration - 1)), "center"),
        "right": lambda t: (max(0, w * (1 - t / duration)), "center"),
        "top": lambda t: ("center", min(0, h * (t / duration - 1))),
        "bottom": lambda t: ("center", max(0, h * (1 - t / duration))),
    }

    return clip.with_position(pos_dict[side])


@requires_duration
def slide_out(clip, duration, side):
    """Makes the clip go away by one side of the screen.

    Only works when the clip is included in a CompositeVideoClip,
    and if the clip has the same size as the whole composition.

    Parameters
    ----------

    clip : moviepy.Clip.Clip
      A video clip.

    duration : float
      Time taken for the clip to fully disappear.

    side : str
      Side of the screen where the clip goes. One of
      'top', 'bottom', 'left' or 'right'.

    Examples
    --------

    >>> clips = [... make a list of clips]
    >>> slided_clips = [
    ...     CompositeVideoClip([clip.fx(transfx.slide_out, 1, "left")])
    ...     for clip in clips
    ... ]
    >>> final_clip = concatenate_videoclips(slided_clips, padding=-1)
    >>>
    >>> clip = ColorClip(
    ...     color=(255, 0, 0), duration=1, size=(300, 300)
    ... ).with_fps(60)
    >>> final_clip = CompositeVideoClip([transfx.slide_out(clip, 1, "right")])
    """
    w, h = clip.size
    ts = clip.duration - duration  # start time of the effect.
    pos_dict = {
        "left": lambda t: (min(0, w * (-(t - ts) / duration)), "center"),
        "right": lambda t: (max(0, w * ((t - ts) / duration)), "center"),
        "top": lambda t: ("center", min(0, h * (-(t - ts) / duration))),
        "bottom": lambda t: ("center", max(0, h * ((t - ts) / duration))),
    }

    return clip.with_position(pos_dict[side])
