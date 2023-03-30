import numpy as np

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.fx.multiply_volume import multiply_volume
from moviepy.decorators import audio_video_fx


@audio_video_fx
def audio_delay(clip, offset=0.2, n_repeats=8, decay=1):
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

    >>> from moviepy import *
    >>> videoclip = AudioFileClip('myaudio.wav').fx(
    ...     audio_delay, offset=.2, n_repeats=10, decayment=.2
    ... )

    >>> # stereo A note
    >>> make_frame = lambda t: np.array(
    ...     [np.sin(440 * 2 * np.pi * t), np.sin(880 * 2 * np.pi * t)]
    ... ).T
    ... clip = AudioClip(make_frame=make_frame, duration=0.1, fps=44100)
    ... clip = audio_delay(clip, offset=.2, n_repeats=11, decay=0)
    """
    decayments = np.linspace(1, max(0, decay), n_repeats + 1)
    return CompositeAudioClip(
        [
            clip.copy(),
            *[
                multiply_volume(
                    clip.with_start((rep + 1) * offset), decayments[rep + 1]
                )
                for rep in range(n_repeats)
            ],
        ]
    )
