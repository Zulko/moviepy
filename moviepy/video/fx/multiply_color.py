from __future__ import annotations

from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from moviepy.video.VideoClip import VideoClip


def multiply_color(clip: VideoClip, factor: float) -> VideoClip:
    """
    Multiplies the clip's colors by the given factor, can be used
    to decrease or increase the clip's brightness (is that the
    right word ?)
    """
    return clip.image_transform(
        lambda frame: np.minimum(255, (factor * frame)).astype("uint8")
    )
