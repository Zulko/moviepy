import numpy as np

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
