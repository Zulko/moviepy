"""Third party programs configuration for MoviePy."""

import os
import subprocess as sp
from pathlib import Path

from moviepy.tools import cross_platform_popen_params


try:
    from dotenv import find_dotenv, load_dotenv

    DOTENV = find_dotenv()
    load_dotenv(DOTENV)
except ImportError:
    DOTENV = None

FFMPEG_BINARY = os.getenv("FFMPEG_BINARY", "ffmpeg-imageio")
FFPLAY_BINARY = os.getenv("FFPLAY_BINARY", "auto-detect")

IS_POSIX_OS = os.name == "posix"


def try_cmd(cmd):
    """Verify if the OS support command invocation as expected by moviepy"""
    try:
        popen_params = cross_platform_popen_params(
            {"stdout": sp.PIPE, "stderr": sp.PIPE, "stdin": sp.DEVNULL}
        )
        proc = sp.Popen(cmd, **popen_params)
        proc.communicate()
    except Exception as err:
        return False, err
    else:
        return True, None


if FFMPEG_BINARY == "ffmpeg-imageio":
    from imageio.plugins.ffmpeg import get_exe

    FFMPEG_BINARY = get_exe()

elif FFMPEG_BINARY == "auto-detect":
    if try_cmd(["ffmpeg"])[0]:
        FFMPEG_BINARY = "ffmpeg"
    elif not IS_POSIX_OS and try_cmd(["ffmpeg.exe"])[0]:
        FFMPEG_BINARY = "ffmpeg.exe"
    else:  # pragma: no cover
        FFMPEG_BINARY = "unset"
else:
    success, err = try_cmd([FFMPEG_BINARY])
    if not success:
        raise IOError(
            f"{err} - The path specified for the ffmpeg binary might be wrong"
        )


if FFPLAY_BINARY == "auto-detect":
    if try_cmd(["ffplay"])[0]:
        FFPLAY_BINARY = "ffplay"
    elif not IS_POSIX_OS and try_cmd(["ffplay.exe"])[0]:
        FFPLAY_BINARY = "ffplay.exe"
    else:  # pragma: no cover
        FFPLAY_BINARY = "unset"
else:
    success, err = try_cmd([FFPLAY_BINARY])
    if not success:
        raise IOError(
            f"{err} - The path specified for the ffmpeg binary might be wrong"
        )


def check():
    """Check if moviepy has found the binaries for FFmpeg."""
    if try_cmd([FFMPEG_BINARY])[0]:
        print(f"MoviePy: ffmpeg successfully found in '{FFMPEG_BINARY}'.")
    else:  # pragma: no cover
        print(f"MoviePy: can't find or access ffmpeg in '{FFMPEG_BINARY}'.")

    if try_cmd([FFPLAY_BINARY])[0]:
        print(f"MoviePy: ffplay successfully found in '{FFPLAY_BINARY}'.")
    else:  # pragma: no cover
        print(f"MoviePy: can't find or access ffplay in '{FFPLAY_BINARY}'.")

    if DOTENV:
        print(f"\n.env file content at {DOTENV}:\n")
        print(Path(DOTENV).read_text())


if __name__ == "__main__":  # pragma: no cover
    check()
