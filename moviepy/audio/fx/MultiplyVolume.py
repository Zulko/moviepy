from dataclasses import dataclass

import numpy as np

from moviepy.Clip import Clip
from moviepy.decorators import audio_video_effect
from moviepy.Effect import Effect
from moviepy.tools import convert_to_seconds


@dataclass
class MultiplyVolume(Effect):
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
    >>> music = AudioFileClip("music.ogg")
    >>> # doubles audio volume
    >>> doubled_audio_clip = music.with_effects([afx.MultiplyVolume(2)])
    >>> # halves audio volume
    >>> half_audio_clip = music.with_effects([afx.MultiplyVolume(0.5)])
    >>> # silences clip during one second at third
    >>> effect = afx.MultiplyVolume(0, start_time=2, end_time=3)
    >>> silenced_clip = clip.with_effects([effect])
    """

    factor: float
    start_time: float = None
    end_time: float = None

    def __post_init__(self):
        if self.start_time is not None:
            self.start_time = convert_to_seconds(self.start_time)

        if self.end_time is not None:
            self.end_time = convert_to_seconds(self.end_time)

    def _multiply_volume_in_range(self, factor, start_time, end_time, nchannels):
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

    @audio_video_effect
    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        if self.start_time is None and self.end_time is None:
            return clip.transform(
                lambda get_frame, t: self.factor * get_frame(t),
                keep_duration=True,
            )

        return clip.transform(
            self._multiply_volume_in_range(
                self.factor,
                clip.start if self.start_time is None else self.start_time,
                clip.end if self.end_time is None else self.end_time,
                clip.nchannels,
            ),
            keep_duration=True,
        )
