"""Imports everything that you need from the MoviePy submodules so that every thing
can be directly imported with ``from moviepy import *``.
"""

from moviepy.audio import fx as afx
from moviepy.audio.AudioClip import (
    AudioArrayClip,
    AudioClip,
    CompositeAudioClip,
    concatenate_audioclips,
)
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.Effect import Effect
from moviepy.tools import convert_to_seconds
from moviepy.version import __version__
from moviepy.video import fx as vfx, tools as videotools
from moviepy.video.compositing.CompositeVideoClip import (
    CompositeVideoClip,
    clips_array,
    concatenate_videoclips,
)
from moviepy.video.io import ffmpeg_tools
from moviepy.video.io.display_in_notebook import display_in_notebook
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import (
    BitmapClip,
    ColorClip,
    DataVideoClip,
    ImageClip,
    TextClip,
    UpdatedVideoClip,
    VideoClip,
)


# Add display in notebook to video and audioclip
VideoClip.display_in_notebook = display_in_notebook
AudioClip.display_in_notebook = display_in_notebook


# Importing with `from moviepy import *` will only import these names
__all__ = [
    "__version__",
    "VideoClip",
    "DataVideoClip",
    "UpdatedVideoClip",
    "ImageClip",
    "ColorClip",
    "TextClip",
    "BitmapClip",
    "VideoFileClip",
    "CompositeVideoClip",
    "clips_array",
    "ImageSequenceClip",
    "concatenate_videoclips",
    "AudioClip",
    "AudioArrayClip",
    "CompositeAudioClip",
    "concatenate_audioclips",
    "AudioFileClip",
    "Effect",
    "vfx",
    "afx",
    "videotools",
    "ffmpeg_tools",
    "convert_to_seconds",
]
