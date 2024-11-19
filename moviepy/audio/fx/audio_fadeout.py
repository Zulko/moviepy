"""Audio fade-out effect for use with moviepy's audio clips.

This module provides a function to create a fade-out effect where audio gradually
decreases from full volume to silence over a specified duration at the end of a clip.
The effect can be applied to both mono and stereo audio clips, and supports time
specifications in various formats through the convert_parameter_to_seconds decorator.
"""

try:
    import numpy as np
except ImportError as exc:
    raise ImportError("MoviePy requires numpy. Please install it with pip install numpy") from exc

from moviepy.decorators import (
    audio_video_fx,
    convert_parameter_to_seconds,
    requires_duration,
)


def _mono_factor_getter(clip_duration):
    return lambda t, duration: np.minimum(1.0 * (clip_duration - t) / duration, 1)


def _stereo_factor_getter(clip_duration, nchannels):
    def getter(t, duration):
        factor = np.minimum(1.0 * (clip_duration - t) / duration, 1)
        return np.array([factor for _ in range(nchannels)]).T

    return getter


@audio_video_fx
@requires_duration
@convert_parameter_to_seconds(["duration"])
def audio_fadeout(clip, duration):
    """Return a sound clip where the sound fades out progressively
    over ``duration`` seconds at the end of the clip.

    Parameters
    ----------

    duration : float
      How long does it take for the sound to reach the zero level at the end
      of the clip.

    Examples
    --------

    >>> clip = VideoFileClip("media/chaplin.mp4")
    >>> clip.fx(audio_fadeout, "00:00:06")
    """
    get_factor = (
        _mono_factor_getter(clip.duration)
        if clip.nchannels == 1
        else _stereo_factor_getter(clip.duration, clip.nchannels)
    )

    return clip.transform(
        lambda get_frame, t: get_factor(t, duration) * get_frame(t),
        keep_duration=True,
    )
