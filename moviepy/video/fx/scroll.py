from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from moviepy.video.VideoClip import VideoClip


def scroll(
    clip: VideoClip,
    w: int | None = None,
    h: int | None = None,
    x_speed: float = 0,
    y_speed: float = 0,
    x_start: float = 0,
    y_start: float = 0,
    apply_to: str = "mask",
) -> VideoClip:
    """
    Scrolls horizontally or vertically a clip, e.g. to make end credits

    Parameters
    ----------

    w, h
      The width and height of the final clip. Default to clip.w and clip.h

    x_speed, y_speed

    x_start, y_start


    apply_to

    """
    if h is None:
        h = clip.h
    if w is None:
        w = clip.w

    x_max = w - 1
    y_max = h - 1

    def filter(get_frame, t):
        x = int(max(0, min(x_max, x_start + round(x_speed * t))))
        y = int(max(0, min(y_max, y_start + round(y_speed * t))))
        return get_frame(t)[y : y + h, x : x + w]

    return clip.transform(filter, apply_to=apply_to)
