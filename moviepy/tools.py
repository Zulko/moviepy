"""Misc. useful functions that can be used at many places in the program."""

import os
import platform
import subprocess as sp
import warnings

import proglog


OS_NAME = os.name


def cross_platform_popen_params(popen_params):
    """Wrap with this function a dictionary of ``subprocess.Popen`` kwargs and
    will be ready to work without unexpected behaviours in any platform.
    Currently, the implementation will add to them:

    - ``creationflags=0x08000000``: no extra unwanted window opens on Windows
      when the child process is created. Only added on Windows.
    """
    if OS_NAME == "nt":
        popen_params["creationflags"] = 0x08000000
    return popen_params


def subprocess_call(cmd, logger="bar"):
    """Executes the given subprocess command.

    Set logger to None or a custom Proglog logger to avoid printings.
    """
    logger = proglog.default_bar_logger(logger)
    logger(message="MoviePy - Running:\n>>> " + " ".join(cmd))

    popen_params = cross_platform_popen_params(
        {"stdout": sp.DEVNULL, "stderr": sp.PIPE, "stdin": sp.DEVNULL}
    )

    proc = sp.Popen(cmd, **popen_params)

    out, err = proc.communicate()  # proc.wait()
    proc.stderr.close()

    if proc.returncode:
        logger(message="MoviePy - Command returned an error")
        raise IOError(err.decode("utf8"))
    else:
        logger(message="MoviePy - Command successful")

    del proc


def ffmpeg_escape_filename(filename):
    """Escape a filename that we want to pass to the ffmpeg command line

    That will ensure the filename doesn't start with a '-' (which would raise an error)
    """
    if filename.startswith("-"):
        filename = "./" + filename

    return filename


def convert_to_seconds(time):
    """Will convert any time into seconds.

    If the type of `time` is not valid,
    it's returned as is.

    Here are the accepted formats:

    .. code:: python

        convert_to_seconds(15.4)   # seconds
        15.4
        convert_to_seconds((1, 21.5))   # (min,sec)
        81.5
        convert_to_seconds((1, 1, 2))   # (hr, min, sec)
        3662
        convert_to_seconds('01:01:33.045')
        3693.045
        convert_to_seconds('01:01:33,5')    # coma works too
        3693.5
        convert_to_seconds('1:33,5')    # only minutes and secs
        99.5
        convert_to_seconds('33.5')      # only secs
        33.5
    """
    factors = (1, 60, 3600)

    if isinstance(time, str):
        time = [float(part.replace(",", ".")) for part in time.split(":")]

    if not isinstance(time, (tuple, list)):
        return time

    return sum(mult * part for mult, part in zip(factors, reversed(time)))


def deprecated_version_of(func, old_name):
    """Indicates that a function is deprecated and has a new name.

    `func` is the new function and `old_name` is the name of the deprecated
    function.

    Returns
    -------

    deprecated_func
      A function that does the same thing as `func`, but with a docstring
      and a printed message on call which say that the function is
      deprecated and that you should use `func` instead.

    Examples
    --------

    .. code:: python

        # The badly named method 'to_file' is replaced by 'write_file'
        class Clip:
            def write_file(self, some args):
                # blablabla
        Clip.to_file = deprecated_version_of(Clip.write_file, 'to_file')
    """
    # Detect new name of func
    new_name = func.__name__

    warning = (
        "The function ``%s`` is deprecated and is kept temporarily "
        "for backwards compatibility.\nPlease use the new name, "
        "``%s``, instead."
    ) % (old_name, new_name)

    def deprecated_func(*args, **kwargs):
        warnings.warn("MoviePy: " + warning, PendingDeprecationWarning)
        return func(*args, **kwargs)

    deprecated_func.__doc__ = warning

    return deprecated_func


# Non-exhaustive dictionary to store default information.
# Any addition is most welcome.
# Note that 'gif' is complicated to place. From a VideoFileClip point of view,
# it is a video, but from a HTML5 point of view, it is an image.

extensions_dict = {
    "mp4": {"type": "video", "codec": ["libx264", "libmpeg4", "aac"]},
    "mkv": {"type": "video", "codec": ["libx264", "libmpeg4", "aac"]},
    "ogv": {"type": "video", "codec": ["libtheora"]},
    "webm": {"type": "video", "codec": ["libvpx"]},
    "avi": {"type": "video"},
    "mov": {"type": "video", "codec": ["libx264", "prores"]},
    "ogg": {"type": "audio", "codec": ["libvorbis"]},
    "mp3": {"type": "audio", "codec": ["libmp3lame"]},
    "wav": {"type": "audio", "codec": ["pcm_s16le", "pcm_s24le", "pcm_s32le"]},
    "m4a": {"type": "audio", "codec": ["libfdk_aac"]},
    "flac": {"type": "audio", "codec": ["flac"]},
}

for ext in ["jpg", "jpeg", "png", "bmp", "tiff"]:
    extensions_dict[ext] = {"type": "image"}


def find_extension(codec):
    """Returns the correspondent file extension for a codec.

    Parameters
    ----------

    codec : str
      Video or audio codec name.
    """
    if codec in extensions_dict:
        # codec is already the extension
        return codec

    for ext, infos in extensions_dict.items():
        if codec in infos.get("codec", []):
            return ext
    raise ValueError(
        "The audio_codec you chose is unknown by MoviePy. "
        "You should report this. In the meantime, you can "
        "specify a temp_audiofile with the right extension "
        "in write_videofile."
    )


def close_all_clips(objects="globals", types=("audio", "video", "image")):
    """Closes all clips in a context.

    Follows different strategies retrieving the namespace from which the clips
    to close will be retrieved depending on the ``objects`` argument, and filtering
    by type of clips depending on the ``types`` argument.

    Parameters
    ----------

    objects : str or dict, optional
      - If is a string an the value is ``"globals"``, will close all the clips
        contained by the ``globals()`` namespace.
      - If is a dictionary, the values of the dictionary could be clips to close,
        useful if you want to use ``locals()``.

    types : Iterable, optional
      Set of types of clips to close, being "audio", "video" or "image" the supported
      values.
    """
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.video.VideoClip import ImageClip

    CLIP_TYPES = {
        "audio": AudioFileClip,
        "video": VideoFileClip,
        "image": ImageClip,
    }

    if objects == "globals":  # pragma: no cover
        objects = globals()
    if hasattr(objects, "values"):
        objects = objects.values()
    types_tuple = tuple(CLIP_TYPES[key] for key in types)
    for obj in objects:
        if isinstance(obj, types_tuple):
            obj.close()


def no_display_available() -> bool:
    """Return True if we determine the host system has no graphical environment.
    This is usefull to remove tests requiring display, like preview

    ..info::
        Currently this only works for Linux/BSD systems with X11 or wayland.
        It probably works for SunOS, AIX and CYGWIN
    """
    system = platform.system()
    if system in ["Linux", "FreeBSD", "NetBSD", "OpenBSD", "SunOS", "AIX"]:
        if ("DISPLAY" not in os.environ) and ("WAYLAND_DISPLAY" not in os.environ):
            return True

    if "CYGWIN_NT" in system:
        if ("DISPLAY" not in os.environ) and ("WAYLAND_DISPLAY" not in os.environ):
            return True

    return False


def compute_position(
    clip1_size: tuple, clip2_size: tuple, pos: any, relative: bool = False
) -> tuple[int, int]:
    """Return the position to put clip 1 on clip 2 based on both clip size
    and the position of clip 1, as return by clip1.pos() method

    Parameters
    ----------
    clip1_size : tuple
        The width and height of clip1 (e.g., (width, height)).
    clip2_size : tuple
        The width and height of clip2 (e.g., (width, height)).
    pos : Any
        The position of clip1 as returned by the `clip1.pos()` method.
    relative: bool
        Is the position relative (% of clip size), default False.

    Returns
    -------
    tuple[int, int]
        A tuple (x, y) representing the top-left corner of clip1 relative to clip2.

    Notes
    -----
    For more information on `pos`, see the documentation for `VideoClip.with_position`.
    """
    if pos is None:
        pos = (0, 0)

    # preprocess short writings of the position
    if isinstance(pos, str):
        pos = {
            "center": ["center", "center"],
            "left": ["left", "center"],
            "right": ["right", "center"],
            "top": ["center", "top"],
            "bottom": ["center", "bottom"],
        }[pos]
    else:
        pos = list(pos)

    # is the position relative (given in % of the clip's size) ?
    if relative:
        for i, dim in enumerate(clip2_size):
            if not isinstance(pos[i], str):
                pos[i] = dim * pos[i]

    if isinstance(pos[0], str):
        D = {
            "left": 0,
            "center": (clip2_size[0] - clip1_size[0]) / 2,
            "right": clip2_size[0] - clip1_size[0],
        }
        pos[0] = D[pos[0]]

    if isinstance(pos[1], str):
        D = {
            "top": 0,
            "center": (clip2_size[1] - clip1_size[1]) / 2,
            "bottom": clip2_size[1] - clip1_size[1],
        }
        pos[1] = D[pos[1]]

    # Return as int, rounding if necessary
    return (int(pos[0]), int(pos[1]))
