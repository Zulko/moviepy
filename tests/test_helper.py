"""Define general test helper attributes and utilities."""

import functools
import sys
import tempfile

from moviepy.video.io.VideoFileClip import VideoFileClip


PYTHON_VERSION = "%s.%s" % (sys.version_info.major, sys.version_info.minor)
TMP_DIR = tempfile.gettempdir()  # because tempfile.tempdir is sometimes None

# Arbitrary font used in caption testing.
if sys.platform in ("win32", "cygwin"):
    FONT = "Arial"
    # Even if Windows users install the Liberation fonts, it is called
    # LiberationMono on Windows, so it doesn't help.
else:
    FONT = (
        "Liberation-Mono"  # This is available in the fonts-liberation package on Linux
    )


@functools.lru_cache(maxsize=None)
def get_test_video():
    return VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0, 1)
