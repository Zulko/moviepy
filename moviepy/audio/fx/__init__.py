"""Audio FX functions for use with moviepy's audio clips.

This module provides a collection of audio effects that can be applied to audio clips
in moviepy. These effects include fading, volume adjustment, delay, normalization,
and looping.

Each function can be applied either by importing it directly from this module
or by using the fx method on an audio clip instance.
"""

from typing import Tuple  # Add type imports first

# Audio effects imports sorted alphabetically
from moviepy.audio.fx.audio_delay import audio_delay
from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.fx.multiply_stereo_volume import multiply_stereo_volume
from moviepy.audio.fx.multiply_volume import multiply_volume


__all__: Tuple[str, ...] = (
    "audio_delay",
    "audio_fadein",
    "audio_fadeout",
    "audio_loop",
    "audio_normalize",
    "multiply_stereo_volume",
    "multiply_volume",
)
