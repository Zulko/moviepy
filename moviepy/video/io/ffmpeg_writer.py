"""
On the long term this will implement several methods to make videos
out of VideoClips
"""

import sys
import numpy as np
import subprocess as sp

from tqdm import tqdm

from moviepy.conf import FFMPEG_BINARY
from moviepy.tools import sys_write_flush


class FFMPEG_VideoWriter:
    """ A class for FFMPEG-based video writing.
    
    A class to write videos using ffmpeg. ffmpeg will write in a large
    choice of formats.
    
    Parameters
    -----------
    
    filename
      Any filename like 'video.mp4' etc. but if you want to avoid
      complications it is recommended to use the generic extension
      '.avi' for all your videos.
    
    size
      Size (width,height) of the output video in pixels.
      
    fps
      Frames per second in the output video file.
      
    codec
      FFMPEG codec. It seems that in terms of quality the hierarchy is
      'rawvideo' = 'png' > 'mpeg4' > 'libx264'
      'png' manages the same lossless quality as 'rawvideo' but yields
      smaller files. Type ``ffmpeg -codecs`` in a terminal to get a list
      of accepted codecs.
      
    bitrate
      Only relevant for codecs which accept a bitrate. "5000k" offers
      nice results in general.
    
    withmask
      Boolean. Set to ``True`` if there is a mask in the video to be
      encoded.
      
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
            
        self.proc = sp.Popen(cmd,stdin=sp.PIPE, stderr=sp.PIPE)
        
    def write_frame(self,img_array):
        """ Writes 1 frame in the file ! """
        self.proc.stdin.write(img_array.tostring())
        #self.proc.stdin.flush()
        
    def close(self):
        self.proc.stdin.close()
        self.proc.stderr.close()
        self.proc.wait()
        
        del self.proc
        
def ffmpeg_write_video(clip, filename, fps, codec="libx264", bitrate=None,
                  withmask=False, verbose=True):
    
    def verbose_print(s):
        if verbose: sys_write_flush(s)
    
    verbose_print("\nWriting video into %s\n"%filename)
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
    
    verbose_print("Done writing video in %s !"%filename)
        
        
def ffmpeg_write_image(filename, image):
    """ Writes an image (HxWx3 or HxWx4 numpy array) to a file, using
        ffmpeg. """
    cmd = [ FFMPEG_BINARY, '-y',
           '-s', "%dx%d"%(image.shape[:2][::-1]),
           "-f", 'rawvideo',
           '-pix_fmt', "rgba" if (image.shape[2] == 4) else "rgb24",
           '-i','-', filename]
           
    proc = sp.Popen( cmd, stdin=sp.PIPE, stderr=sp.PIPE)
    proc.stdin.write(image.tostring())
    proc.stdin.close()
    proc.communicate() # proc.wait()
    
    if proc.returncode:
        err = "\n".join(["MoviePy running : %s"%cmd,
                          "WARNING: this command returned an error:",
                          proc.stderr.read().decode('utf8')])
        raise IOError(err)
    
    del proc
