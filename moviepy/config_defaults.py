"""
Configuration MoviePy


This file enables you to specify a configuration for MoviePy. In
particular you can enter the path to the FFMPEG and ImageMagick
binaries.

Note that at any time in a script you can change the value of these
variables as follows:

>>> import moviepy.config as cf
>>> cf.change_settings({"FFMPEG_BINARY": "some/new/path/to/ffmpeg"})
>>> print( cf.get_setting("FFMPEG_BINARY") )  # prints the current setting

Instructions
--------------


FFMPEG_BINARY
    Normally you can leave this one to its default ('auto-detect') and MoviePy
    will detect automatically the right name, which will be either
    'ffmpeg' (on linux) or 'ffmpeg.exe' (on windows). If you want to
    use a binary at a special location on you disk, enter it like that:

    FFMPEG_BINARY = r"path/to/ffmpeg" # on linux
    FFMPEG_BINARY = r"path\to\ffmpeg.exe" # on windows

    Warning: the 'r' before the path is important, especially on Windows.


IMAGEMAGICK_BINARY
    For linux users, 'convert' should be fine.
    For Windows users, you must specify the path to the ImageMagick
    'convert' binary. For instance:

    IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-6.8.8-Q16\convert.exe"

"""

FFMPEG_BINARY = 'auto-detect'
IMAGEMAGICK_BINARY = 'convert'