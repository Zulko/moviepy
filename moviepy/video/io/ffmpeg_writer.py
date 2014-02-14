"""
On the long term this will implement several methods to make videos
out of VideoClips
"""

import sys
import numpy as np
import subprocess as sp

from tqdm import tqdm

from moviepy.conf import FFMPEG_BINARY


class FFMPEG_VideoWriter:
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
    
    
        
    def __init__(self, filename, size, fps, codec="libx264",
                  bitrate=None, withmask=False):
        
        self.filename = filename
        cmd = [ FFMPEG_BINARY, '-y',
            "-f", 'rawvideo',
            "-vcodec","rawvideo",
            '-s', "%dx%d"%(size[0],size[1]),
            '-pix_fmt', "rgba" if withmask else "rgb24",
            '-r', "%.02f"%fps,
            '-i', '-', '-an',
            '-vcodec', codec] + (
            ['-b',bitrate] if (bitrate!=None) else []) + [
            '-r', "%d"%fps,
            filename ]
        self.proc = sp.Popen(cmd,stdin=sp.PIPE,
                                 stdout=sp.PIPE,
                                 stderr=sp.PIPE)
        
    def write_frame(self,img_array):
        self.proc.stdin.write(img_array.tostring())
        #img_array.tofile(self.proc.stdin) only python 2.7
        
    def close(self):
        self.proc.stdin.close()
        self.proc.wait()
        del self.proc
        
def ffmpeg_write(clip, filename, fps, codec="libx264", bitrate=None,
                  withmask=False, verbose=True):
    
    if verbose:
        def verbose_print(s):
            sys.stdout.write(s)
            sys.stdout.flush()
    else:
        verbose_print = lambda *a : None
    
    verbose_print("Rendering video %s\n"%filename)
    writer = FFMPEG_VideoWriter(filename, clip.size, fps, codec = codec,
             bitrate=bitrate)
             
    nframes = int(clip.duration*fps)
    
    for i in tqdm(range(nframes)):
        frame = clip.get_frame(1.0*i/fps)
        if withmask:
            mask = (255*clip.mask.get_frame(1.0*i/fps))
            frame = np.dstack([frame,mask])
            
        writer.write_frame(frame.astype("uint8"))
    
    writer.close()
    verbose_print("video done !")
        
        
def write_image(filename, image):
    """ Writes an image (HxWx3 or HxWx4 numpy array) to a file, using
        ffmpeg. """
    proc = sp.Popen([ FFMPEG_BINARY, '-y',
            '-s', "%dx%d"%(image.shape[:2][::-1]),
            "-f", 'rawvideo',
            '-pix_fmt', "rgba" if (image.shape[2] == 4) else "rgb24",
            '-i','-', filename],
            stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    image.tofile(proc.stdin)
    proc.stdin.close()
    proc.wait()
    del proc
