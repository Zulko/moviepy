"""
This file is meant to make it easy to load the main features of MoviePy
by simply typing: from moviepy.all import *
"""

# Note that these imports could have been performed in the __init__.py
# file, but this would make the loading of moviepy slower.

# Clips

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import VideoClip, ImageClip, ColorClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate
from moviepy.audio.io.AudioFileClip import AudioFileClip

# FX

import moviepy.video.fx as vfx
import moviepy.audio.fx as afx
import moviepy.video.compositing.transitions as transfx

# Tools

import moviepy.video.tools as videotools
import moviepy.video.io.ffmpeg_tools as ffmpeg_tools
from moviepy.tools import cvsecs
