from __future__ import division

import sys
import numpy as np
import subprocess as sp

try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

from tqdm import tqdm
from moviepy.conf import FFMPEG_BINARY
from moviepy.decorators import requires_duration

from moviepy.tools import sys_write_flush

class FFMPEG_AudioWriter:
    """
    A class to write an AudioClip into an audio file.
    
    Parameters
    ------------
    
    filename
      Name of any video or audio file, like ``video.mp4`` or ``sound.wav`` etc.
    
    size
      Size (width,height) in pixels of the output video.
    
    fps_input
      Frames per second of the input audio (given by the AUdioClip being
      written down).
    
    codec
      Name of the ffmpeg codec to use for the output.
    
    bitrate:
      A string indicating the bitrate of the final video. Only
      relevant for codecs which accept a bitrate.
      
    """
    
    
        
    def __init__(self, filename, fps_input, nbytes=2,
                 nchannels = 2, codec='libfdk_aac', bitrate=None,
                 input_video=None,logfile=None):
        
        self.filename = filename

        if logfile is None:
          logfile = DEVNULL

        cmd = ([ FFMPEG_BINARY, '-y',
            "-loglevel", "panic" if logfile==DEVNULL else "info",
            "-f", 's%dle'%(8*nbytes),
            "-acodec",'pcm_s%dle'%(8*nbytes),
            '-ar', "%d"%fps_input,
            '-ac',"%d"%nchannels,
            '-i', '-']
            + (['-vn'] if input_video==None else
                 [ "-i", input_video, '-vcodec', 'copy'])
            + ['-acodec', codec]
            + ['-ar', "%d"%fps_input]
            + ['-strict', '-2']  # needed to support codec 'aac'
            + (['-ab',bitrate] if (bitrate!=None) else [])
            + [ filename ])
        

        self.proc = sp.Popen(cmd, stdin=sp.PIPE,
                                  stderr=logfile,
                                  stdout=DEVNULL)

        
    def write_frames(self,frames_array):
        self.proc.stdin.write(frames_array.tostring())
        
        
    def close(self):
        self.proc.stdin.close()
        #self.proc.stderr.close()
        #self.proc.stdout.close()
        self.proc.wait()
        del self.proc
        
        
        
@requires_duration       
def ffmpeg_audiowrite(clip, filename, fps, nbytes, buffersize,
                      codec='libvorbis', bitrate=None,
                      write_logfile = False, verbose=True):
    """
    A function that wraps the FFMPEG_AudioWriter to write an AudioClip
    to a file.
    """
    
    def verbose_print(s):
        if verbose: sys_write_flush(s)

    if write_logfile:
        logfile = open(filename + ".log", 'w+')
    else:
        logfile = DEVNULL
        
    verbose_print("Writing audio in %s\n"%filename)
     
    writer = FFMPEG_AudioWriter(filename, fps, nbytes, clip.nchannels,
                                codec=codec, bitrate=bitrate,
                                logfile=logfile)
                                
    totalsize = int(fps*clip.duration)
    
    if (totalsize % buffersize == 0):
        nchunks = totalsize // buffersize
    else:
        nchunks = totalsize // buffersize + 1
        
    pospos = list(range(0, totalsize,  buffersize))+[totalsize]
    
    for i in tqdm(range(nchunks)):
        tt = (1.0/fps)*np.arange(pospos[i],pospos[i+1])
        sndarray = clip.to_soundarray(tt, nbytes= nbytes)
        writer.write_frames(sndarray)


    writer.close()
    
    if write_logfile:
        logfile.close()

    verbose_print("Done writing Audio in %s !\n"%filename)
