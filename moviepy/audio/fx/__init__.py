# import every video fx function

from moviepy.audio.fx.audio_delay import audio_delay
from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.fx.multiply_stereo_volume import multiply_stereo_volume
from moviepy.audio.fx.multiply_volume import multiply_volume


__all__ = (
    "audio_delay",
    "audio_fadein",
    "audio_fadeout",
    "audio_loop",
    "audio_normalize",
    "multiply_stereo_volume",
    "multiply_volume",
)
