from dataclasses import dataclass

import numpy as np

from moviepy.Clip import Clip
from moviepy.decorators import audio_video_effect
from moviepy.Effect import Effect
from moviepy.tools import convert_to_seconds


@dataclass
class AudioFadeIn(Effect):
    """Return an audio (or video) clip that is first mute, then the
    sound arrives progressively over ``duration`` seconds.

    Parameters
    ----------

    duration : float
        How long does it take for the sound to return to its normal level.

    Examples
    --------

    .. code:: python

        clip = VideoFileClip("media/chaplin.mp4")
        clip.with_effects([afx.AudioFadeIn("00:00:06")])
    """

    duration: float

    def __post_init__(self):
        self.duration = convert_to_seconds(self.duration)

    def _mono_factor_getter(self):
        return lambda t, duration: np.minimum(t / duration, 1)

    def _stereo_factor_getter(self, nchannels):
        def getter(t, duration):
            factor = np.minimum(t / duration, 1)
            return np.array([factor for _ in range(nchannels)]).T

        return getter

    @audio_video_effect
    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        if clip.duration is None:
            raise ValueError("Attribute 'duration' not set")

        get_factor = (
            self._mono_factor_getter()
            if clip.nchannels == 1
            else self._stereo_factor_getter(clip.nchannels)
        )

        return clip.transform(
            lambda get_frame, t: get_factor(t, self.duration) * get_frame(t),
        )
