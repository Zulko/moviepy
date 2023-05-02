from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from moviepy.video.VideoClip import VideoClip


def invert_colors(clip: VideoClip) -> VideoClip:
    """Returns the color-inversed clip.

    The values of all pixels are replaced with (255-v) or (1-v) for masks
    Black becomes white, green becomes purple, etc.
    """
    maxi = 1.0 if clip.is_mask else 255
    return clip.image_transform(lambda f: maxi - f)
