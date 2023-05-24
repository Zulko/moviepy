from __future__ import annotations

from typing import TYPE_CHECKING

import moviepy.video.compositing.transitions as transfx
from moviepy.decorators import requires_duration
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

if TYPE_CHECKING:
    from moviepy.video.VideoClip import VideoClip


@requires_duration
def make_loopable(clip: VideoClip, overlap_duration: float) -> CompositeVideoClip:
    """Makes the clip fade in progressively at its own end, this way it can be
    looped indefinitely.

    Parameters
    ----------

    overlap_duration : float
      Duration of the fade-in (in seconds).
    """
    clip2 = clip.fx(transfx.crossfadein, overlap_duration).with_start(
        clip.duration - overlap_duration
    )
    return CompositeVideoClip([clip, clip2]).subclip(overlap_duration, clip.duration)
