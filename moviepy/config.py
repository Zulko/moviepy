import os
from pathlib import Path
import subprocess as sp


if os.name == "nt":
    import winreg as wr

try:
    from dotenv import load_dotenv, find_dotenv

    DOTENV = find_dotenv()
    load_dotenv(DOTENV)
except ImportError:
    DOTENV = None

FFMPEG_BINARY = os.getenv("FFMPEG_BINARY", "ffmpeg-imageio")
IMAGEMAGICK_BINARY = os.getenv("IMAGEMAGICK_BINARY", "auto-detect")


def try_cmd(cmd):
    try:
        popen_params = {"stdout": sp.PIPE, "stderr": sp.PIPE, "stdin": sp.DEVNULL}

        # This was added so that no extra unwanted window opens on windows
        # when the child process is created
        if os.name == "nt":
            popen_params["creationflags"] = 0x08000000

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
    elif try_cmd(["ffmpeg.exe"])[0]:
        FFMPEG_BINARY = "ffmpeg.exe"
    else:
        FFMPEG_BINARY = "unset"
else:
    success, err = try_cmd([FFMPEG_BINARY])
    if not success:
        raise IOError(
            f"{err} - The path specified for the ffmpeg binary might be wrong"
        )

if IMAGEMAGICK_BINARY == "auto-detect":
    if os.name == "nt":
        # Try a few different ways of finding the ImageMagick binary on Windows
        try:
            key = wr.OpenKey(wr.HKEY_LOCAL_MACHINE, "SOFTWARE\\ImageMagick\\Current")
            IMAGEMAGICK_BINARY = wr.QueryValueEx(key, "BinPath")[0] + r"\magick.exe"
            key.Close()
        except Exception:
            try:
                imagemagick_path = sp.check_output(
                    r'dir /B /O-N "C:\Program Files\ImageMagick-*"',
                    shell=True,
                    encoding="utf-8",
                ).split("\n")[0]
                IMAGEMAGICK_BINARY = sp.check_output(
                    rf'dir /B /S "C:\Program Files\{imagemagick_path}\*convert.exe"',
                    shell=True,
                    encoding="utf-8",
                ).split("\n")[0]
            except Exception:
                IMAGEMAGICK_BINARY = "unset"

    elif try_cmd(["convert"])[0]:
        IMAGEMAGICK_BINARY = "convert"

    else:
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
    if try_cmd([FFMPEG_BINARY])[0]:
        print(f"MoviePy: ffmpeg successfully found in '{FFMPEG_BINARY}'.")
    else:
        print(f"MoviePy: can't find or access ffmpeg in '{FFMPEG_BINARY}'.")

    if try_cmd([IMAGEMAGICK_BINARY])[0]:
        print(f"MoviePy: ImageMagick successfully found in '{IMAGEMAGICK_BINARY}'.")
    else:
        print(f"MoviePy: can't find or access ImageMagick in '{IMAGEMAGICK_BINARY}'.")

    if DOTENV:
        print(f"\n.env file content at {DOTENV}:\n")
        print(Path(DOTENV).read_text())


if __name__ == "__main__":
    check()
