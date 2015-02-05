"""
Configuration of MoviePy


This file enables you to specify a configuration for MoviePy. In
particular you can enter the path to the FFMPEG and ImageMagick
binaries.

These changes must be done BEFORE installing MoviePy: first make the changes,
then install MoviePy with

    [sudo] python setup.py install

Note that you can also change the path to the binaries AFTER installation, but
only for one script at a time, as follows:

>>> import moviepy.config as cf
>>> cf.change_settings({"FFMPEG_BINARY": "some/new/path/to/ffmpeg"})
>>> print( cf.get_setting("FFMPEG_BINARY") )  # prints the current setting


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

FFMPEG_BINARY = 'ffmpeg-imageio'
IMAGEMAGICK_BINARY = 'auto-detect'