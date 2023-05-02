from typing import TYPE_CHECKING

from __future__ import annotations

from moviepy.decorators import apply_to_audio, apply_to_mask, requires_duration


if TYPE_CHECKING:
    from moviepy.video.VideoClip import VideoClip


@requires_duration
@apply_to_mask
@apply_to_audio
def time_mirror(clip: VideoClip) -> VideoClip:
    """
    Returns a clip that plays the current clip backwards.
    The clip must have its ``duration`` attribute set.
    The same effect is applied to the clip's audio and mask if any.
    """
    return clip.time_transform(lambda t: clip.duration - t - 1, keep_duration=True)
