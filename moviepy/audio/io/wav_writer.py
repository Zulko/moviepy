import sys
import wave
import numpy as np
import subprocess as sp

def wave_write(clip, filename,fps, nbytes, buffersize, verbose):
    """ Writes an audioclip down to a wav file. Deprecated if the
        ffmpeg writer works as expected. Otherwise, a good safety wheel
    """
    if verbose:
        def verbose_print(s):
            sys.stdout.write(s)
            sys.stdout.flush()
    else:
        verbose_print = lambda *a : None
        
    verbose_print("Rendering audio %s\n"%filename)
     
    totalsize = int(fps*clip.duration)
    # initialize the wave file with Python's wave module
    wavf = wave.open(filename, 'wb')
    wavf.setnchannels(clip.nchannels)
    wavf.setsampwidth(nbytes)
    wavf.setframerate(fps)
    wavf.setnframes(totalsize)
    
    # Simply append chunks with Python's open
    nchunks = totalsize / buffersize + 1
    pospos = np.array(list(range(0, totalsize,  buffersize))+[totalsize])
    ifeedback = max(1,nchunks/10)
    for i in range(nchunks):
        if ( (i% ifeedback) == 0): verbose_print("=")
        tt = (1.0/fps)*np.arange(pospos[i],pospos[i+1])
        sndarray = clip.to_soundarray(tt,nbytes)
        wavf.writeframes(sndarray.tostring())
    wavf.close()
    
    verbose_print("audio done!")
