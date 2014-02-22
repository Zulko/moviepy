from __future__ import division

import sys
import numpy as np
import subprocess as sp

from tqdm import tqdm
from moviepy.conf import FFMPEG_BINARY
from moviepy.decorators import requires_duration


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
    
    
        
    def __init__(self, filename, fps_input, nbytes=2, nchannels = 2,
                  codec='libfdk_aac', bitrate=None, input_video=None):
        
        self.filename = filename
        cmd = ([ FFMPEG_BINARY, '-y',
            "-f", 's%dle'%(8*nbytes),
            "-acodec",'pcm_s%dle'%(8*nbytes),
            '-r', "%d"%fps_input,
            '-ac',"%d"%nchannels,
            '-i', '-']
            + (['-vn'] if input_video==None else
                 [ "-i", input_video, '-vcodec', 'copy'])
            + ['-acodec', codec]
            + (['-b',bitrate] if (bitrate!=None) else [])
            + [ filename ])
        self.proc = sp.Popen(cmd,stdin=sp.PIPE,
                                 stderr=sp.PIPE)
        
    def write_frames(self,frames_array):
        self.proc.stdin.write(frames_array.tostring())
        
    def close(self):
        self.proc.stdin.close()
        self.proc.stderr.close()
        del self.proc
        
        
        
@requires_duration       
def ffmpeg_audiowrite(clip, filename, fps, nbytes, buffersize,
                      codec='libvorbis', bitrate=None, verbose=True):
    """
    A function that wraps the FFMPEG_AudioWriter to write an AudioClip
    to a file.
    """
    
    if verbose:
        def verbose_print(s):
            sys.stdout.write(s)
            sys.stdout.flush()
    else:
        verbose_print = lambda *a : None
        
    verbose_print("Writing audio in %s\n"%filename)
     
    writer = FFMPEG_AudioWriter(filename, fps, nbytes, clip.nchannels,
                                codec=codec, bitrate=bitrate)
                                
    totalsize = int(fps*clip.duration)
    nchunks = totalsize // buffersize + 1
    pospos = np.array(list(range(0, totalsize,  buffersize))+[totalsize])
    
    for i in tqdm(range(nchunks)):
        tt = (1.0/fps)*np.arange(pospos[i],pospos[i+1])
        sndarray = clip.to_soundarray(tt,nbytes)
        writer.write_frames(sndarray)
    
    writer.close()
    verbose_print("Done writing Audio in %s !\n"%filename)
