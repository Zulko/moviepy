"""
Misc. useful functions that can be used at many places in the program.
"""

import subprocess as sp
import sys


def sys_write_flush(s):
    """ writes and flushes without delay a text in the console """
    sys.stdout.write(s)
    sys.stdout.flush()


def subprocess_call(cmd, verbose=True, errorprint=True):
    """
    executes the subprocess command
    """
    
    def verboseprint(s):
        if verbose: sys_write_flush(s)
    
    verboseprint( "\nMoviePy Running:\n>>> "+ " ".join(cmd) )
    
    proc = sp.Popen(cmd, stderr = sp.PIPE)
                         
    out, err = proc.communicate() # proc.wait()
    proc.stderr.close()
    
    if proc.returncode:
        if errorprint:
            sys_write_flush( "\nMoviePy: WARNING !\n"
                    "   The following command returned an error:\n")
            sys_write_flush( err.decode('utf8'))
        raise IOError(err.decode('utf8'))
    else:
        verboseprint( "\n... command successful.\n")
    
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
