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

    .. code:: python

        from moviepy import AudioFileClip

        music = AudioFileClip("music.ogg")
        # doubles audio volume
        doubled_audio_clip = music.with_effects([afx.MultiplyVolume(2)])
        # halves audio volume
        half_audio_clip = music.with_effects([afx.MultiplyVolume(0.5)])
        # silences clip during one second at third
        effect = afx.MultiplyVolume(0, start_time=2, end_time=3)
        silenced_clip = clip.with_effects([effect])
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
            # `t` is usually a NumPy array (audio chunk times). Keep this fast and
            # avoid Python loops.
            if np.isscalar(t):
                return factor if (start_time <= t <= end_time) else 1.0
            t_arr = np.asarray(t)
            mask = (t_arr >= start_time) & (t_arr <= end_time)
            return np.where(mask, factor, 1.0)

        def multiply_stereo_volume(get_frame, t):
            a = factors_filter(factor, t)
            fr = get_frame(t)
            if np.isscalar(a):
                return np.multiply(fr, a)
            return np.multiply(fr, a[:, None])

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
