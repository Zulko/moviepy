"""
Imports everything that you need from the MoviePy submodules so that every thing
can be directly imported like `from moviepy import VideoFileClip`.

In particular it loads all effects from the video.fx and audio.fx folders
and turns them into VideoClip and AudioClip methods, so that instead of
``clip.fx(vfx.resize, 2)`` or ``vfx.resize(clip, 2)``
you can write ``clip.resize(2)``.

"""

import inspect

from moviepy.version import __version__


# Clips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.video.io.downloader import download_webfile
from moviepy.video.VideoClip import (
    VideoClip,
    ImageClip,
    ColorClip,
    TextClip,
    BitmapClip,
)
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip, clips_array
from moviepy.video.compositing.concatenate import concatenate_videoclips

from moviepy.audio.AudioClip import (
    AudioClip,
    CompositeAudioClip,
    concatenate_audioclips,
)
from moviepy.audio.io.AudioFileClip import AudioFileClip

# FX
from moviepy.video import fx as vfx
import moviepy.audio.fx as afx
import moviepy.video.compositing.transitions as transfx

# Tools
import moviepy.video.tools as videotools
import moviepy.video.io.ffmpeg_tools as ffmpeg_tools
from moviepy.tools import convert_to_seconds


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
