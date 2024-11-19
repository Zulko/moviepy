"""Audio fade-in effect for use with moviepy's audio clips.

This module provides a function to create a fade-in effect where audio gradually
increases from silence to full volume over a specified duration. The effect can
be applied to both mono and stereo audio clips, and supports time specifications
in various formats through the convert_parameter_to_seconds decorator.
"""

from typing import Callable, Union

try:
    import numpy as np
    from numpy.typing import NDArray
except ImportError as exc:
    raise ImportError("MoviePy requires numpy. Please install it with pip install numpy") from exc

from moviepy.decorators import audio_video_fx, convert_parameter_to_seconds


def _create_mono_fade_factor() -> Callable[[float, float], float]:
    """Create a fade factor function for mono audio.
    
    Returns
    -------
    Callable[[float, float], float]
        A function that takes time and duration and returns a fade factor.
    """
    return lambda t, duration: np.minimum(t / duration, 1)


def _create_stereo_fade_factor(nchannels: int) -> Callable[[float, float], NDArray]:
    """Create a fade factor function for stereo/multi-channel audio.
    
    Parameters
    ----------
    nchannels : int
        Number of audio channels.

    Returns
    -------
    Callable[[float, float], NDArray]
        A function that takes time and duration and returns an array of fade factors.
    """
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
        _create_mono_fade_factor()
        if clip.nchannels == 1
        else _create_mono_fade_factor(clip.nchannels)
    )

    return clip.transform(
        lambda get_frame, t: get_factor(t, duration) * get_frame(t),
        keep_duration=True,
    )
