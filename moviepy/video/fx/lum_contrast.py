from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from moviepy.video.VideoClip import VideoClip


def lum_contrast(
    clip: VideoClip, lum: int = 0, contrast: int = 0, contrast_threshold: int = 127
) -> VideoClip:
    """Luminosity-contrast correction of a clip."""

    def image_filter(im):
        im = 1.0 * im  # float conversion
        corrected = im + lum + contrast * (im - float(contrast_threshold))
        corrected[corrected < 0] = 0
        corrected[corrected > 255] = 255
        return corrected.astype("uint8")

    return clip.image_transform(image_filter)
