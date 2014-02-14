"""
Name (and location if needed) of the FFMPEG binary. It will be
"ffmpeg" on linux, certainly "ffmpeg.exe" on windows, else any path.
If not provided (None), the system will look for the right version
automatically each time you launch moviepy.
If you run this script file it will check that the
path to the ffmpeg binary (FFMPEG_BINARY)
"""

FFMPEG_BINARY = None



# --------------------------------------------------------------------

import subprocess as sp

def tryffmpeg(FFMPEG_BINARY):    
        try:
            proc = sp.Popen([FFMPEG_BINARY],
                             stdout=sp.PIPE,
                             stderr=sp.PIPE)
            proc.wait()
        except:
            return False
        else:
            return True


if FFMPEG_BINARY is None:
    
    if tryffmpeg('ffmpeg'):
        FFMPEG_BINARY = 'ffmpeg'
    elif tryffmpeg('ffmpeg.exe'):
        FFMPEG_BINARY = 'ffmpeg.exe'
    else:
        raise IOError("FFMPEG binary not found. Try installing MoviePy"\
                       " manually and specify the path to the binary in"\
                       " the file conf.py")


if __name__ == "__main__":
    if tryffmpeg(FFMPEG_BINARY):
        print( "MoviePy : ffmpeg successfully found." )
    else:
        print( "MoviePy : can't find ffmpeg." )
        
        
