from __future__ import annotations

from typing import TYPE_CHECKING

from moviepy.decorators import apply_to_mask, requires_duration
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.time_mirror import time_mirror

if TYPE_CHECKING:
    from moviepy.video.VideoClip import VideoClip


@requires_duration
@apply_to_mask
def time_symmetrize(clip: VideoClip) -> VideoClip:
    """
    Returns a clip that plays the current clip once forwards and
    then once backwards. This is very practival to make video that
    loop well, e.g. to create animated GIFs.
    This effect is automatically applied to the clip's mask and audio
    if they exist.
    """
    return concatenate_videoclips([clip, clip.fx(time_mirror)])
