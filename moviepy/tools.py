"""Misc. useful functions that can be used at many places in the program."""
import os
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
    logger(message="Moviepy - Running:\n>>> " + " ".join(cmd))

    popen_params = cross_platform_popen_params(
        {"stdout": sp.DEVNULL, "stderr": sp.PIPE, "stdin": sp.DEVNULL}
    )

    proc = sp.Popen(cmd, **popen_params)

    out, err = proc.communicate()  # proc.wait()
    proc.stderr.close()

    if proc.returncode:
        logger(message="Moviepy - Command returned an error")
        raise IOError(err.decode("utf8"))
    else:
        logger(message="Moviepy - Command successful")

    del proc


def convert_to_seconds(time):
    """Will convert any time into seconds.

    If the type of `time` is not valid,
    it's returned as is.

    Here are the accepted formats:

    >>> convert_to_seconds(15.4)   # seconds
    15.4
    >>> convert_to_seconds((1, 21.5))   # (min,sec)
    81.5
    >>> convert_to_seconds((1, 1, 2))   # (hr, min, sec)
    3662
    >>> convert_to_seconds('01:01:33.045')
    3693.045
    >>> convert_to_seconds('01:01:33,5')    # coma works too
    3693.5
    >>> convert_to_seconds('1:33,5')    # only minutes and secs
    99.5
    >>> convert_to_seconds('33.5')      # only secs
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

    >>> # The badly named method 'to_file' is replaced by 'write_file'
    >>> class Clip:
    >>>    def write_file(self, some args):
    >>>        # blablabla
    >>>
    >>> Clip.to_file = deprecated_version_of(Clip.write_file, 'to_file')
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
    "mov": {"type": "video"},
    "ogg": {"type": "audio", "codec": ["libvorbis"]},
    "mp3": {"type": "audio", "codec": ["libmp3lame"]},
    "wav": {"type": "audio", "codec": ["pcm_s16le", "pcm_s24le", "pcm_s32le"]},
    "m4a": {"type": "audio", "codec": ["libfdk_aac"]},
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
