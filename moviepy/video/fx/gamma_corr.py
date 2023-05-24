from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from moviepy.video.VideoClip import VideoClip


def gamma_corr(clip: VideoClip, gamma: int) -> VideoClip:
    """Gamma-correction of a video clip."""

    def filter(im):
        corrected = 255 * (1.0 * im / 255) ** gamma
        return corrected.astype("uint8")

    return clip.image_transform(filter)
