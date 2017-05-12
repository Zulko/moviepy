"""
Configuration of MoviePy


This file enables you to specify a configuration for MoviePy. In
particular you can enter the path to the FFMPEG and ImageMagick
binaries.

Defaults must be done BEFORE installing MoviePy: first make the changes,
then install MoviePy with

    [sudo] python setup.py install

Note that you can also change the path by setting environment variables.
e.g.

Linux/Mac:
   export FFMPEG_BINARY=path/to/ffmpeg

Windows:
   set FFMPEG_BINARY=path\to\ffmpeg

Instructions
--------------

FFMPEG_BINARY
    Normally you can leave this one to its default ('ffmpeg-imageio') at which
    case image-io will download the right ffmpeg binary (at first use) and then
    always use that binary.
    The second option is 'auto-detect', in this case ffmpeg will be whatever
    binary is found on the computer generally 'ffmpeg' (on linux) or 'ffmpeg.exe'
    (on windows).
    Third option: If you want to use a binary at a special location on you disk,
    enter it like that:

    FFMPEG_BINARY = r"path/to/ffmpeg" # on linux
    FFMPEG_BINARY = r"path\to\ffmpeg.exe" # on windows

    Warning: the 'r' before the path is important, especially on Windows.


IMAGEMAGICK_BINARY
    For linux users, 'convert' should be fine.
    For Windows users, you must specify the path to the ImageMagick
    'convert' binary. For instance:

    IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-6.8.8-Q16\convert.exe"

"""

import os

FFMPEG_BINARY = os.getenv('FFMPEG_BINARY', 'ffmpeg-imageio')
IMAGEMAGICK_BINARY = os.getenv('IMAGEMAGICK_BINARY', 'auto-detect')