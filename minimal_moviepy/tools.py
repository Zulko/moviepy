"""
Misc. useful functions that can be used at many places in the program.
"""
import sys


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
    
    if isinstance(time, str):     
        time = [float(f.replace(',', '.')) for f in time.split(':')]

    if not isinstance(time, (tuple, list)):
        return time

    return sum(mult * part for mult, part in zip(factors, reversed(time)))


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
