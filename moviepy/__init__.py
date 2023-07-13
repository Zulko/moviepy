"""Imports everything that you need from the MoviePy submodules so that every thing
can be directly imported like `from moviepy import VideoFileClip`.

In particular it loads all effects from the video.fx and audio.fx folders
and turns them into VideoClip and AudioClip methods, so that instead of
``clip.fx(vfx.resize, 2)`` or ``vfx.resize(clip, 2)``
you can write ``clip.resize(2)``.
"""

import inspect

from moviepy.audio import fx as afx
from moviepy.audio.AudioClip import (
    AudioClip,
    CompositeAudioClip,
    AudioArrayClip,
    concatenate_audioclips,
)
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.tools import convert_to_seconds
from moviepy.version import __version__
from moviepy.video import fx as vfx, tools as videotools
from moviepy.video.compositing import transitions as transfx
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip, clips_array, concatenate_videoclips
from moviepy.video.io import ffmpeg_tools
from moviepy.video.io.display_in_notebook import display_in_notebook
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy import Effect
from moviepy.video.VideoClip import (
    BitmapClip,
    ColorClip,
    ImageClip,
    TextClip,
    VideoClip,
    DataVideoClip,
    UpdatedVideoClip,
)


# Transforms the effects into Clip methods so that
# they can be called with clip.resize(width=500) instead of
# clip.fx(vfx.resize, width=500)
audio_fxs = inspect.getmembers(afx, inspect.isfunction) + [("Loop", vfx.Loop)]
video_fxs = (
    inspect.getmembers(vfx, inspect.isfunction)
    + inspect.getmembers(transfx, inspect.isfunction)
    + audio_fxs
)

for name, function in video_fxs:
    setattr(VideoClip, name, function)

for name, function in audio_fxs:
    setattr(AudioClip, name, function)

# Add display in notebook to video and audioclip
VideoClip.display_in_notebook = display_in_notebook
AudioClip.display_in_notebook = display_in_notebook

# Cleanup namespace
del audio_fxs, video_fxs, name, function
del inspect

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
    "vfx",
    "afx",
    "transfx",
    "videotools",
    "ffmpeg_tools",
    "convert_to_seconds",
]
