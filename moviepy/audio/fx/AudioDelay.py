from dataclasses import dataclass

import numpy as np

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
from moviepy.Clip import Clip
from moviepy.decorators import audio_video_effect
from moviepy.Effect import Effect


@dataclass
class AudioDelay(Effect):
    """Repeats audio certain number of times at constant intervals multiplying
    their volume levels using a linear space in the range 1 to ``decay`` argument
    value.

    Parameters
    ----------

    offset : float, optional
      Gap between repetitions start times, in seconds.

    n_repeats : int, optional
      Number of repetitions (without including the clip itself).

    decay : float, optional
      Multiplication factor for the volume level of the last repetition. Each
      repetition will have a value in the linear function between 1 and this value,
      increasing or decreasing constantly. Keep in mind that the last repetition
      will be muted if this is 0, and if is greater than 1, the volume will increase
      for each repetition.

    Examples
    --------

    .. code:: python

        from moviepy import *
        videoclip = AudioFileClip('myaudio.wav').with_effects([
            afx.AudioDelay(offset=.2, n_repeats=10, decayment=.2)
        ])

        # stereo A note
        frame_function = lambda t: np.array(
            [np.sin(440 * 2 * np.pi * t), np.sin(880 * 2 * np.pi * t)]
        ).T
        clip = AudioClip(frame_function=frame_function, duration=0.1, fps=44100)
        clip = clip.with_effects([afx.AudioDelay(offset=.2, n_repeats=11, decay=0)])
    """

    offset: float = 0.2
    n_repeats: int = 8
    decay: float = 1

    @audio_video_effect
    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        decayments = np.linspace(1, max(0, self.decay), self.n_repeats + 1)
        return CompositeAudioClip(
            [
                clip.copy(),
                *[
                    clip.with_start((rep + 1) * self.offset).with_effects(
                        [MultiplyVolume(decayments[rep + 1])]
                    )
                    for rep in range(self.n_repeats)
                ],
            ]
        )
