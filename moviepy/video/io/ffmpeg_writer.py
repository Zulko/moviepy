"""
On the long term this will implement several methods to make videos
out of VideoClips
"""

import numpy as np
import subprocess as sp

try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')



from tqdm import tqdm

from moviepy.conf import FFMPEG_BINARY
from moviepy.tools import verbose_print




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

      Note for default 'libx264': by default the pixel format yuv420p
      is used. If the video dimensions are not both even (e.g. 720x405)
      another pixel format is used, and this can cause problem in some
      video readers.
    
    preset
      Sets the time that FFMPEG will take to compress the video. The slower,
      the better the compression rate. Possibilities are: ultrafast,superfast,
      veryfast, faster, fast, medium (default), slow, slower, veryslow, placebo.

    bitrate
      Only relevant for codecs which accept a bitrate. "5000k" offers
      nice results in general.
    
    withmask
      Boolean. Set to ``True`` if there is a mask in the video to be
      encoded.
      
    """
    
    
        
    def __init__(self, filename, size, fps, codec="libx264",
                 preset="medium", bitrate=None, withmask=False,
                 logfile=None):

        if logfile is None:
          logfile = sp.PIPE

        self.filename = filename
        self.codec = codec
        self.ext = self.filename.split(".")[-1]

        cmd = (
            [ FFMPEG_BINARY, '-y',
            "-loglevel", "error" if logfile==sp.PIPE else "info",
            "-f", 'rawvideo',
            "-vcodec","rawvideo",
            '-s', "%dx%d"%(size[0],size[1]),
            '-pix_fmt', "rgba" if withmask else "rgb24",
            '-r', "%.02f"%fps,
            '-i', '-', '-an',
            '-vcodec', codec,
            '-preset', preset]
            + (['-b',bitrate] if (bitrate!=None) else [])

            # http://trac.ffmpeg.org/ticket/658
            + (['-pix_fmt', 'yuv420p']
                  if ((codec == 'libx264') and
                     (size[0]%2 == 0) and
                     (size[1]%2 == 0))
                     
               else [])

            + [ '-r', "%d"%fps, filename ]
            )

        self.proc = sp.Popen(cmd, stdin=sp.PIPE,
                                  stderr=logfile,
                                  stdout=DEVNULL)

        
    def write_frame(self,img_array):
        """ Writes one frame in the file."""
        try:
            self.proc.stdin.write(img_array.tostring())
        except IOError as err:
            ffmpeg_error = self.proc.stderr.read()
            error = (str(err)+ ("\n\nMoviePy error: FFMPEG encountered "
                     "the following error while writing file %s:"%self.filename
                     + "\n\n"+ffmpeg_error))

            if "Unknown encoder" in ffmpeg_error:
                
                error = error+("\n\nThe video export "
                  "failed because FFMPEG didn't find the specified "
                  "codec for video encoding (%s). Please install "
                  "this codec or change the codec when calling "
                  "write_videofile. For instance:\n"
                  "  >>> clip.write_videofile('myvid.webm', codec='libvpx')")%(self.codec)
            
            elif "incorrect codec parameters ?" in ffmpeg_error:

                 error = error+("\n\nThe video export "
                  "failed, possibly because the codec specified for "
                  "the video (%s) is not compatible with the given "
                  "extension (%s). Please specify a valid 'codec' "
                  "argument in write_videofile. This would be 'libx264' "
                  "or 'mpeg4' for mp4, 'libtheora' for ogv, 'libvpx' "
                  "for webm.")%(self.codec, self.ext)

            elif  "encoder setup failed":

                error = error+("\n\nThe video export "
                  "failed, possibly because the bitrate you specified "
                  "was too high or too low for the video codec.")
            
            raise IOError(error)
        
    def close(self):
        self.proc.stdin.close()
        if self.proc.stderr is not None:
            self.proc.stderr.close()
        self.proc.wait()
        
        del self.proc
        
def ffmpeg_write_video(clip, filename, fps, codec="libx264", bitrate=None,
                       preset = "medium", withmask=False, write_logfile=False,
                       verbose=True):
    
    if write_logfile:
        logfile = open(filename + ".log", 'w+')
    else:
        logfile = None


    verbose_print(verbose, "\nWriting video into %s\n"%filename)
    writer = FFMPEG_VideoWriter(filename, clip.size, fps, codec = codec,
                                preset=preset, bitrate=bitrate,
                                logfile=logfile)
             
    nframes = int(clip.duration*fps)
    
    for t,frame in clip.iter_frames(progress_bar=True, with_times=True,
                                    fps=fps):
        if withmask:
            mask = 255*clip.mask.get_frame(t)
            frame = np.dstack([frame,mask])
            
        writer.write_frame(frame.astype("uint8"))
    
    writer.close()

    if write_logfile:
      logfile.close()
    
    verbose_print(verbose, "Done writing video in %s !"%filename)
        
        
def ffmpeg_write_image(filename, image, logfile=False):
    """ Writes an image (HxWx3 or HxWx4 numpy array) to a file, using
        ffmpeg. """


    cmd = [ FFMPEG_BINARY, '-y',
           '-s', "%dx%d"%(image.shape[:2][::-1]),
           "-f", 'rawvideo',
           '-pix_fmt', "rgba" if (image.shape[2] == 4) else "rgb24",
           '-i','-', filename]
    
    if logfile: 
        log_file = open(filename + ".log", 'w+')
    else:
        log_file = sp.PIPE


    proc = sp.Popen( cmd, stdin=sp.PIPE, stderr=log_file)
    proc.communicate(image.tostring()) # proc.wait()
    
    if proc.returncode:
        err = "\n".join(["MoviePy running : %s"%cmd,
                          "WARNING: this command returned an error:",
                          proc.stderr.read().decode('utf8')])
        raise IOError(err)


    
    del proc
