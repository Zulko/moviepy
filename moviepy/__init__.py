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
    concatenate_audioclips,
)
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.tools import convert_to_seconds
from moviepy.version import __version__
from moviepy.video import fx as vfx, tools as videotools
from moviepy.video.compositing import transitions as transfx
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip, clips_array
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io import ffmpeg_tools
from moviepy.video.io.downloader import download_webfile
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import (
    BitmapClip,
    ColorClip,
    ImageClip,
    TextClip,
    VideoClip,
)


# Transforms the effects into Clip methods so that
# they can be called with clip.resize(width=500) instead of
# clip.fx(vfx.resize, width=500)
audio_fxs = inspect.getmembers(afx, inspect.isfunction) + [("loop", vfx.loop)]
video_fxs = (
    inspect.getmembers(vfx, inspect.isfunction)
    + inspect.getmembers(transfx, inspect.isfunction)
    + audio_fxs
)

for name, function in video_fxs:
    setattr(VideoClip, name, function)

for name, function in audio_fxs:
    setattr(AudioClip, name, function)


def preview(self, *args, **kwargs):
    """NOT AVAILABLE: clip.preview requires importing from moviepy.editor"""
    raise ImportError("clip.preview requires importing from moviepy.editor")


def show(self, *args, **kwargs):
    """NOT AVAILABLE: clip.show requires importing from moviepy.editor"""
    raise ImportError("clip.show requires importing from moviepy.editor")


VideoClip.preview = preview
VideoClip.show = show
AudioClip.preview = preview

# Cleanup namespace
del audio_fxs, video_fxs, name, function, preview, show
del inspect

# Importing with `from moviepy import *` will only import these names
__all__ = [
    "__version__",
    "VideoClip",
    "ImageClip",
    "ColorClip",
    "TextClip",
    "BitmapClip",
    "VideoFileClip",
    "CompositeVideoClip",
    "clips_array",
    "ImageSequenceClip",
    "concatenate_videoclips",
    "download_webfile",
    "AudioClip",
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
