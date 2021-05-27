"""Define general test helper attributes and utilities."""

import contextlib
import functools
import http.server
import socketserver
import sys
import tempfile
import threading

import numpy as np

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


@functools.lru_cache(maxsize=None)
def get_stereo_wave(left_freq=440, right_freq=220):
    def make_stereo_frame(t):
        return np.array(
            [np.sin(left_freq * 2 * np.pi * t), np.sin(right_freq * 2 * np.pi * t)]
        ).T.copy(order="C")

    return make_stereo_frame


@functools.lru_cache(maxsize=None)
def get_mono_wave(freq=440):
    def make_mono_frame(t):
        return np.sin(freq * 2 * np.pi * t)

    return make_mono_frame


@contextlib.contextmanager
def static_files_server(port=8000):
    class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
        pass

    my_server = socketserver.TCPServer(("", port), MyHttpRequestHandler)
    thread = threading.Thread(target=my_server.serve_forever, daemon=True)
    thread.start()
    yield thread
