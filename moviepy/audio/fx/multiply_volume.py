from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from moviepy.decorators import audio_video_fx, convert_parameter_to_seconds

if TYPE_CHECKING:
    from moviepy.audio.AudioClip import AudioClip


def _multiply_volume_in_range(
    factor: float, start_time: float, end_time: float, nchannels: int
):
    def factors_filter(factor, t):
        return np.array([factor if start_time <= t_ <= end_time else 1 for t_ in t])

    def multiply_stereo_volume(get_frame, t):
        return np.multiply(
            get_frame(t),
            np.array([factors_filter(factor, t) for _ in range(nchannels)]).T,
        )

    def multiply_mono_volume(get_frame, t):
        return np.multiply(get_frame(t), factors_filter(factor, t))

    return multiply_mono_volume if nchannels == 1 else multiply_stereo_volume


@audio_video_fx
@convert_parameter_to_seconds(["start_time", "end_time"])
def multiply_volume(
    clip: AudioClip,
    factor: float,
    start_time: float | None = None,
    end_time: float | None = None,
) -> AudioClip:
    """Returns a clip with audio volume multiplied by the
    value `factor`. Can be applied to both audio and video clips.

    Parameters
    ----------

    factor : float
      Volume multiplication factor.

    start_time : float, optional
      Time from the beginning of the clip until the volume transformation
      begins to take effect, in seconds. By default at the beginning.

    end_time : float, optional
      Time from the beginning of the clip until the volume transformation
      ends to take effect, in seconds. By default at the end.

    Examples
    --------

    >>> from moviepy import AudioFileClip
    >>>
    >>> music = AudioFileClip('music.ogg')
    >>> doubled_audio_clip = clip.multiply_volume(2)  # doubles audio volume
    >>> half_audio_clip = clip.multiply_volume(0.5)  # half audio
    >>>
    >>> # silenced clip during one second at third
    >>> silenced_clip = clip.multiply_volume(0, start_time=2, end_time=3)
    """
    if start_time is None and end_time is None:
        return clip.transform(
            lambda get_frame, t: factor * get_frame(t),
            keep_duration=True,
        )

    return clip.transform(
        _multiply_volume_in_range(
            factor,
            clip.start if start_time is None else start_time,
            clip.end if end_time is None else end_time,
            clip.nchannels,
        ),
        keep_duration=True,
    )
