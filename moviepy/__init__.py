"""Imports everything that you need from the MoviePy submodules so that every thing
can be directly imported like `from moviepy import VideoFileClip`.

In particular it loads all effects from the video.fx and audio.fx folders
and turns them into VideoClip and AudioClip methods, so that instead of
``clip.fx(vfx.resize, 2)`` or ``vfx.resize(clip, 2)``
you can write ``clip.resize(2)``.
"""

import inspect
import copy

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
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip, clips_array, concatenate_videoclips
from moviepy.video.io import ffmpeg_tools
from moviepy.video.io.display_in_notebook import display_in_notebook
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.Effect import Effect
from moviepy.video.VideoClip import (
    BitmapClip,
    ColorClip,
    ImageClip,
    TextClip,
    VideoClip,
    DataVideoClip,
    UpdatedVideoClip,
)

import re


# Black magic to transforms the effects into Clip methods so that
# they can be called with clip.resize(width=500) instead of
# clip.with_effect(vfx.Resize(width=500))
# We use a lot of inspect + closure + setattr + python scope magic 
audio_fxs = inspect.getmembers(afx, inspect.isclass)
video_fxs = inspect.getmembers(vfx, inspect.isclass) + audio_fxs

def add_effect_as_method(to_klass, method_name, eklass) :
    def effect_call(clip, *args, **kwargs):
        return clip.with_effect(eklass(*args, **kwargs).copy())
    
    setattr(to_klass, method_name, effect_call)

for name, effect_class in video_fxs :
    camel_name = re.sub('(?!^)([A-Z]+)', r'_\1', name).lower()
    add_effect_as_method(VideoClip, camel_name, effect_class)

for name, effect_class in audio_fxs :
    camel_name = re.sub('(?!^)([A-Z]+)', r'_\1', name).lower()
    add_effect_as_method(AudioClip, camel_name, effect_class)

# Add display in notebook to video and audioclip
VideoClip.display_in_notebook = display_in_notebook
AudioClip.display_in_notebook = display_in_notebook

# Cleanup namespace
del audio_fxs, video_fxs, inspect, add_effect_as_method

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
