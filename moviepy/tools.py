"""
Misc. useful functions that can be used at many places in the program.
"""

import subprocess as sp
import sys
import warnings


def sys_write_flush(s):
    """ Writes and flushes without delay a text in the console """
    sys.stdout.write(s)
    sys.stdout.flush()


def verbose_print(verbose, s):
    """ Only prints s (with sys_write_flush) if verbose is True."""
    if verbose:
        sys_write_flush(s)


def subprocess_call(cmd, verbose=True, errorprint=True):
    """ Executes the given subprocess command."""

    verbose_print(verbose, "\nMoviePy Running:\n>>> "+ " ".join(cmd))
    
    proc = sp.Popen(cmd, stderr = sp.PIPE)
                         
    out, err = proc.communicate() # proc.wait()
    proc.stderr.close()
    
    if proc.returncode:
        verbose_print(errorprint, "\nMoviePy: This command returned an error !")
        raise IOError(err.decode('utf8'))
    else:
        verbose_print(verbose, "\n... command successful.\n")
    
    del proc


def cvsecs(*args):
    """
    Converts a time to second. Either cvsecs(min,secs) or
    cvsecs(hours,mins,secs).
    >>> cvsecs(5.5) # -> 5.5 seconds
    >>> cvsecs(10, 4.5) # -> 604.5 seconds
    >>> cvsecs(1, 0, 5) # -> 3605 seconds
    """
    if len(args) == 1:
        return args[0]
    elif len(args) == 2:
        return 60*args[0]+args[1]
    elif len(args) ==3:
        return 3600*args[0]+60*args[1]+args[2]


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