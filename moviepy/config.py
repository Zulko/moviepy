"""Third party programs configuration for MoviePy."""

import os
import subprocess as sp
from pathlib import Path

from moviepy.tools import cross_platform_popen_params


if os.name == "nt":
    import winreg as wr

try:
    from dotenv import find_dotenv, load_dotenv

    DOTENV = find_dotenv()
    load_dotenv(DOTENV)
except ImportError:
    DOTENV = None

FFMPEG_BINARY = os.getenv("FFMPEG_BINARY", "ffmpeg-imageio")
IMAGEMAGICK_BINARY = os.getenv("IMAGEMAGICK_BINARY", "auto-detect")

IS_POSIX_OS = os.name == "posix"


def try_cmd(cmd):
    """TODO: add documentation"""
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


def detect_imagemagick_for_windows():
    """Detects imagemagick binary for Windows."""
    try:
        # When the key does not exist, it will raise OSError.
        key = wr.OpenKey(wr.HKEY_LOCAL_MACHINE, r"SOFTWARE\ImageMagick\Current")
        imagemagick_dir = Path(wr.QueryValueEx(key, "BinPath")[0])
        key.Close()
    except OSError:
        # Find it under C:\Program Files\ImageMagick-xxx directory.
        imagemagick_dirs = [
            d
            for d in Path(r"C:\Program Files").iterdir()
            if d.name.startswith("ImageMagick-")
        ]
        if not imagemagick_dirs:
            return "unset"

        # No matter how many versions the user installed, we use the first, because
        # IMAGEMAGICK_BINARY can be specified through environmental variable.
        imagemagick_dir = imagemagick_dirs[0]

    # Get convert.exe or magick.exe under the directory.
    for imagemagick_filename in ["convert.exe", "magick.exe"]:
        p = imagemagick_dir / imagemagick_filename
        if p.exists():
            return str(p)

    # Return unset instead of raising an exception
    # is to try other ways to detect.
    return "unset"


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

if IMAGEMAGICK_BINARY == "auto-detect":
    if os.name == "nt":
        IMAGEMAGICK_BINARY = detect_imagemagick_for_windows()  # pragma: no cover

    if IMAGEMAGICK_BINARY in ["unset", "auto-detect"]:
        if try_cmd(["convert"])[0]:
            IMAGEMAGICK_BINARY = "convert"
        elif not IS_POSIX_OS and try_cmd(["convert.exe"])[0]:  # pragma: no cover
            IMAGEMAGICK_BINARY = "convert.exe"
        else:  # pragma: no cover
            IMAGEMAGICK_BINARY = "unset"
else:
    if not os.path.exists(IMAGEMAGICK_BINARY):
        raise IOError(f"ImageMagick binary cannot be found at {IMAGEMAGICK_BINARY}")

    if not os.path.isfile(IMAGEMAGICK_BINARY):
        raise IOError(f"ImageMagick binary found at {IMAGEMAGICK_BINARY} is not a file")
    success, err = try_cmd([IMAGEMAGICK_BINARY])
    if not success:
        raise IOError(
            f"{err} - The path specified for the ImageMagick binary might "
            f"be wrong: {IMAGEMAGICK_BINARY}"
        )


def check():
    """Check if moviepy has found the binaries of FFmpeg and ImageMagick."""
    if try_cmd([FFMPEG_BINARY])[0]:
        print(f"MoviePy: ffmpeg successfully found in '{FFMPEG_BINARY}'.")
    else:  # pragma: no cover
        print(f"MoviePy: can't find or access ffmpeg in '{FFMPEG_BINARY}'.")

    if try_cmd([IMAGEMAGICK_BINARY])[0]:
        print(f"MoviePy: ImageMagick successfully found in '{IMAGEMAGICK_BINARY}'.")
    else:  # pragma: no cover
        print(f"MoviePy: can't find or access ImageMagick in '{IMAGEMAGICK_BINARY}'.")

    if DOTENV:
        print(f"\n.env file content at {DOTENV}:\n")
        print(Path(DOTENV).read_text())


if __name__ == "__main__":  # pragma: no cover
    check()
