""" Operations with ImageMagick. Still in the making."""

import os
import subprocess
from moviepy.tools import subprocess_call

def gif_to_directory(gif_file,dirName=None):
    """

    POSSIBLY VERY DEPRECATED AND BUGGY

    Stores all the frames of the given .gif file
    into the directory ``dirName``. If ``dirName``
    is not provided, the directory has the same name
    as the .gif file. Supports transparency.
    Returns the directory name.

    Example:

    >>> d = gif_to_directory("animated-earth.gif")
    >>> clip = DirectoryClip(d,fps=3)

    """

    if dirName is None:
        name, ext = os.path.splitext(gif_file)
        dirName = name

    try:
        os.mkdir(dirName)
    except:
        pass

    subprocess_call(["convert", "-coalesce", gif_file,
             os.path.join(dirName,"%04d.png")])
