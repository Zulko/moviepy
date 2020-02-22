"""
Misc. useful functions that can be used at many places in the program.
"""
import os
import subprocess as sp
import sys
import warnings

import proglog

from .compat import DEVNULL



def sys_write_flush(s):
    """ Writes and flushes without delay a text in the console """
    # Reason for not using `print` is that in some consoles "print" 
    # commands get delayed, while stdout.flush are instantaneous, 
    # so this method is better at providing feedback.
    # See https://github.com/Zulko/moviepy/pull/485
    sys.stdout.write(s)
    sys.stdout.flush()


def verbose_print(verbose, s):
    """ Only prints s (with sys_write_flush) if verbose is True."""
    if verbose:
        sys_write_flush(s)


def subprocess_call(cmd, logger='bar', errorprint=True):
    """ Executes the given subprocess command.
    
    Set logger to None or a custom Proglog logger to avoid printings.
    """
    logger = proglog.default_bar_logger(logger)
    logger(message='Moviepy - Running:\n>>> "+ " ".join(cmd)')

    popen_params = {"stdout": DEVNULL,
                    "stderr": sp.PIPE,
                    "stdin": DEVNULL}

    if os.name == "nt":
        popen_params["creationflags"] = 0x08000000

    proc = sp.Popen(cmd, **popen_params)

    out, err = proc.communicate() # proc.wait()
    proc.stderr.close()

    if proc.returncode:
        if errorprint:
            logger(message='Moviepy - Command returned an error')
        raise IOError(err.decode('utf8'))
    else:
        logger(message='Moviepy - Command successful')

    del proc

def is_string(obj):
    """ Returns true if s is string or string-like object,
    compatible with Python 2 and Python 3."""
    try:
        return isinstance(obj, basestring)
    except NameError:
        return isinstance(obj, str)


def cvsecs(time):
    """ Will convert any time into seconds. 
    
    If the type of `time` is not valid, 
    it's returned as is. 

    Here are the accepted formats::

    >>> cvsecs(15.4)   # seconds 
    15.4 
    >>> cvsecs((1, 21.5))   # (min,sec) 
    81.5 
    >>> cvsecs((1, 1, 2))   # (hr, min, sec)  
    3662  
    >>> cvsecs('01:01:33.045') 
    3693.045
    >>> cvsecs('01:01:33,5')    # coma works too
    3693.5
    >>> cvsecs('1:33,5')    # only minutes and secs
    99.5
    >>> cvsecs('33.5')      # only secs
    33.5
    """
    factors = (1, 60, 3600)
    
    if is_string(time):     
        time = [float(f.replace(',', '.')) for f in time.split(':')]

    if not isinstance(time, (tuple, list)):
        return time

    return sum(mult * part for mult, part in zip(factors, reversed(time)))


def deprecated_version_of(f, oldname, newname=None):
    """ Indicates that a function is deprecated and has a new name.

    `f` is the new function, `oldname` the name of the deprecated
    function, `newname` the name of `f`, which can be automatically
    found.

    Returns
    ========

    f_deprecated
      A function that does the same thing as f, but with a docstring
      and a printed message on call which say that the function is
      deprecated and that you should use f instead.

    Examples
    =========

    >>> # The badly named method 'to_file' is replaced by 'write_file'
    >>> class Clip:
    >>>    def write_file(self, some args):
    >>>        # blablabla
    >>>
    >>> Clip.to_file = deprecated_version_of(Clip.write_file, 'to_file')
    """

    if newname is None: newname = f.__name__

    warning= ("The function ``%s`` is deprecated and is kept temporarily "
              "for backwards compatibility.\nPlease use the new name, "
              "``%s``, instead.")%(oldname, newname)

    def fdepr(*a, **kw):
        warnings.warn("MoviePy: " + warning, PendingDeprecationWarning)
        return f(*a, **kw)
    fdepr.__doc__ = warning

    return fdepr


# non-exhaustive dictionnary to store default informations.
# any addition is most welcome.
# Note that 'gif' is complicated to place. From a VideoFileClip point of view,
# it is a video, but from a HTML5 point of view, it is an image.

extensions_dict = { "mp4":  {'type':'video', 'codec':['libx264','libmpeg4', 'aac']},
                    'ogv':  {'type':'video', 'codec':['libtheora']},
                    'webm': {'type':'video', 'codec':['libvpx']},
                    'avi':  {'type':'video'},
                    'mov':  {'type':'video'},

                    'ogg':  {'type':'audio', 'codec':['libvorbis']},
                    'mp3':  {'type':'audio', 'codec':['libmp3lame']},
                    'wav':  {'type':'audio', 'codec':['pcm_s16le', 'pcm_s24le', 'pcm_s32le']},
                    'm4a':  {'type':'audio', 'codec':['libfdk_aac']}
                  }

for ext in ["jpg", "jpeg", "png", "bmp", "tiff"]:
    extensions_dict[ext] = {'type':'image'}


def find_extension(codec):
    if codec in extensions_dict:
        # codec is already the extension
        return codec

    for ext,infos in extensions_dict.items():
        if codec in infos.get('codec', []):
            return ext
    raise ValueError(
        "The audio_codec you chose is unknown by MoviePy. "
        "You should report this. In the meantime, you can "
        "specify a temp_audiofile with the right extension "
        "in write_videofile."
    )
