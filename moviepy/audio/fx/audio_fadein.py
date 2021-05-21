import numpy as np

from moviepy.decorators import audio_video_fx, convert_parameter_to_seconds


def _mono_factor_getter():
    return lambda t, duration: np.minimum(t / duration, 1)


def _stereo_factor_getter(nchannels):
    def getter(t, duration):
        factor = np.minimum(t / duration, 1)
        return np.array([factor for _ in range(nchannels)]).T

    return getter


@audio_video_fx
@convert_parameter_to_seconds(["duration"])
def audio_fadein(clip, duration):
    """Return an audio (or video) clip that is first mute, then the
    sound arrives progressively over ``duration`` seconds.

    Parameters
    ----------

    duration : float
      How long does it take for the sound to return to its normal level.

    Examples
    --------

    >>> clip = VideoFileClip("media/chaplin.mp4")
    >>> clip.fx(audio_fadein, "00:00:06")
    """
    get_factor = (
        _mono_factor_getter()
        if clip.nchannels == 1
        else _stereo_factor_getter(clip.nchannels)
    )

    return clip.transform(
        lambda get_frame, t: get_factor(t, duration) * get_frame(t),
        keep_duration=True,
    )
