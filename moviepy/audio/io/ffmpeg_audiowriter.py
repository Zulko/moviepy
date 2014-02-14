from __future__ import division

import sys
import wave
import numpy as np
import subprocess as sp

from tqdm import tqdm
from moviepy.conf import FFMPEG_BINARY
from moviepy.decorators import requires_duration


class FFMPEG_AudioWriter:
    """ A class to read videos using ffmpeg. ffmpeg will read any kind
        of videos and transform them into raw data (a long string that
        can be reshaped into a RGB array).
        
        :param filename: Any filename like 'video.mp4' etc. but if you
           want to avoid complications it is recommended to use the
           generic extension '.avi' for all your videos.
        :param size: size (width,height) of the output video.
        :param fps: frames per second of the output video.
        :param codec: ffmpeg codec. It seems that in terms of quality
            the hierarchy is
        
            'rawvideo' = 'png' > 'mpeg4' > 'libx264'
        
            'png' manages the same lossless quality as 'rawvideo' but
            yields smaller files.
        
            (type ffmpeg -codecs in a terminal)
        :param bitrate: only relevant for codecs which accept a bitrate
           bitrate = "5000k" offers nice results in general
        :param withmask: True if there is a mask in the video to be
            decoded.
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
                                 stdout=sp.PIPE,
                                 stderr=sp.PIPE)
        
    def write_frames(self,frames_array):
        self.proc.stdin.write(frames_array.tostring())
        #frames_array.tofile(self.proc.stdin) # only python 2.7
        
    def close(self):
        self.proc.stdin.close()
        del self.proc
        
        
        
@requires_duration       
def ffmpeg_audiowrite(clip, filename, fps, nbytes, buffersize,
                      codec='libvorbis', bitrate=None, verbose=True):
    if verbose:
        def verbose_print(s):
            sys.stdout.write(s)
            sys.stdout.flush()
    else:
        verbose_print = lambda *a : None
        
    verbose_print("Rendering audio %s\n"%filename)
     
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
    verbose_print("audio done !")
