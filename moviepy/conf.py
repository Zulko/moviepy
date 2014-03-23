"""
Instructions
--------------

This file enables you to specify a configuration for MoviePy. In
particular you can enter the path to the FFMPEG and ImageMagick
binaries.

FFMPEG_BINARY
    Normally you can leave this one to its default (None) and MoviePy
    will detect automatically the right name, which will be either
    'ffmpeg' (on linux) or 'ffmpeg.exe' (on windows)
    
IMAGEMAGICK_BINARY
    For linux users, 'convert' should be fine.
    For Windows users, you must specify the path to the ImageMagick
    'convert' binary. For instance:
    "C:\Program Files\ImageMagick-6.8.8-Q16\convert" 

You can run this file to check that FFMPEG has been detected.
"""

FFMPEG_BINARY = None
IMAGEMAGICK_BINARY = 'convert'



# =====================================================================
# CODE. Don't write anything below this line :O

import subprocess as sp

def try_cmd(cmd):    
        try:
            proc = sp.Popen(cmd,
                             stdout=sp.PIPE,
                             stderr=sp.PIPE)
            proc.communicate()
        except:
            return False
        else:
            return True


if FFMPEG_BINARY is None:
    
    if try_cmd(['ffmpeg']):
        FFMPEG_BINARY = 'ffmpeg'
    elif try_cmd(['ffmpeg.exe']):
        FFMPEG_BINARY = 'ffmpeg.exe'
    else:
        raise IOError("FFMPEG binary not found. Try installing MoviePy"\
                       " manually and specify the path to the binary in"\
                       " the file conf.py")

if __name__ == "__main__":
    if try_cmd([FFMPEG_BINARY]):
        print( "MoviePy : ffmpeg successfully found." )
    else:
        print( "MoviePy : can't find ffmpeg." )
        
        
