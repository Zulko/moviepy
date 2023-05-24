from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from moviepy.video.VideoClip import VideoClip


def mirror_y(clip: VideoClip, apply_to: str = "mask") -> VideoClip:
    """Flips the clip vertically (and its mask too, by default)."""
    return clip.image_transform(lambda img: img[::-1], apply_to=apply_to)
