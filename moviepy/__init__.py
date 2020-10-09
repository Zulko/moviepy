"""
Imports everything that you need from the MoviePy submodules so that every thing
can be directly imported like `from moviepy import VideoFileClip`.

In particular it loads all effects from the video.fx and audio.fx folders
and turns them into VideoClip and AudioClip methods, so that instead of
``clip.fx(vfx.resize, 2)`` or ``vfx.resize(clip, 2)``
you can write ``clip.resize(2)``.

"""

import os
import inspect

from .version import __version__


# Hide the welcome message from pygame: https://github.com/pygame/pygame/issues/542
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# Clips
from .video.io.VideoFileClip import VideoFileClip
from .video.io.ImageSequenceClip import ImageSequenceClip
from .video.io.downloader import download_webfile
from .video.VideoClip import VideoClip, ImageClip, ColorClip, TextClip, BitmapClip
from .video.compositing.CompositeVideoClip import CompositeVideoClip, clips_array
from .video.compositing.concatenate import concatenate_videoclips

from .audio.AudioClip import AudioClip, CompositeAudioClip, concatenate_audioclips
from .audio.io.AudioFileClip import AudioFileClip

# FX
from .video import fx as vfx
import moviepy.audio.fx as afx
import moviepy.video.compositing.transitions as transfx

# Tools
import moviepy.video.tools as videotools
import moviepy.video.io.ffmpeg_tools as ffmpeg_tools
from .tools import convert_to_seconds


# Transforms the effects into Clip methods so that
# they can be called with clip.resize(width=500) instead of
# clip.fx(vfx.resize, width=500)
audio_fxs = inspect.getmembers(afx, inspect.isfunction)
video_fxs = (
    inspect.getmembers(vfx, inspect.isfunction)
    + inspect.getmembers(transfx, inspect.isfunction)
    + audio_fxs
)

for name, function in video_fxs:
    setattr(VideoClip, name, function)

for name, function in audio_fxs:
    setattr(AudioClip, name, function)

# Cleanup namespace
del audio_fxs, video_fxs, name, function
del os, inspect
