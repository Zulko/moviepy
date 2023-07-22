"""All the audio effects that can be applied to AudioClip and VideoClip."""

# import every video fx function

from moviepy.audio.fx.AudioDelay import AudioDelay
from moviepy.audio.fx.AudioFadeIn import AudioFadeIn
from moviepy.audio.fx.AudioFadeOut import AudioFadeOut
from moviepy.audio.fx.AudioLoop import AudioLoop
from moviepy.audio.fx.AudioNormalize import AudioNormalize
from moviepy.audio.fx.MultiplyStereoVolume import MultiplyStereoVolume
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume


__all__ = (
    "AudioDelay",
    "AudioFadeIn",
    "AudioFadeOut",
    "AudioLoop",
    "AudioNormalize",
    "MultiplyStereoVolume",
    "MultiplyVolume",
)
