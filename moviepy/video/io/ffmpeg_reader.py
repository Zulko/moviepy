from __future__ import division

import subprocess as sp
import re

import numpy as np
from moviepy.conf import FFMPEG_BINARY  # ffmpeg, ffmpeg.exe, etc...
from moviepy.tools import cvsecs


class FFMPEG_VideoReader:

    def __init__(self, filename, print_infos=False, bufsize = None,
                 pix_fmt="rgb24"):

        self.filename = filename
        self.load_infos(print_infos)
        self.pix_fmt = pix_fmt
        if pix_fmt == 'rgba':
            self.depth = 4
        else:
            self.depth = 3

        if bufsize is None:
            w, h = self.size
            bufsize = self.depth * w * h + 100

        self.proc= None
        self.bufsize= bufsize
        self.initialize()


        self.pos = 1
        self.lastread = self.read_frame()

    def initialize(self, starttime=0):
        """Opens the file, creates the pipe. """
        
        self.close() # if any
        
        if starttime !=0 :
            offset = min(1,starttime)
            i_arg = ['-ss', "%.03f" % (starttime - offset),
                    '-i', self.filename,
                    '-ss', "%.03f" % offset]
        else:
            i_arg = [ '-i', self.filename]
        
        
        cmd = ([FFMPEG_BINARY]+ i_arg +
                ['-loglevel', 'error', 
                '-f', 'image2pipe',
                "-pix_fmt", self.pix_fmt,
                '-vcodec', 'rawvideo', '-'])
        
        
        self.proc = sp.Popen(cmd, bufsize= self.bufsize,
                                   stdout=sp.PIPE,
                                   stderr=sp.PIPE)
                                   
    
    def load_infos(self, print_infos=False):
        """Get file infos using ffmpeg.
        
        Grabs the FFMPEG info on the file and use them to set the
        attributes ``self.size`` and ``self.fps`` """
            
        # open the file in a pipe, provoke an error, read output
        proc = sp.Popen([FFMPEG_BINARY, "-i", self.filename, "-"],
                bufsize=10**6,
                stdout=sp.PIPE,
                stderr=sp.PIPE)
        proc.stdout.readline()
        proc.terminate()
        infos = proc.stderr.read().decode('utf8')
        if print_infos:
            # print the whole info text returned by FFMPEG
            print( infos )

        lines = infos.splitlines()
        if "No such file or directory" in lines[-1]:
            raise IOError("%s not found ! Wrong path ?" % self.filename)

        # get the output line that speaks about video
        line = [l for l in lines if ' Video: ' in l][0]

        # get the size, of the form 460x320 (w x h)
        match = re.search(" [0-9]*x[0-9]*(,| )", line)
        self.size = list(map(int, line[match.start():match.end()-1].split('x')))

        # get the frame rate
        match = re.search("( [0-9]*.| )[0-9]* (tbr|fps)", line)
        self.fps = float(line[match.start():match.end()].split(' ')[1])

        # get duration (in seconds)
        line = [l for l in lines if 'Duration: ' in l][0]
        match = re.search(" [0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9]", line)
        hms = map(float, line[match.start()+1:match.end()].split(':'))
        duration = cvsecs(*hms)
        self.nframes = int(duration*self.fps)
        self.duration = self.nframes / self.fps



    def skip_frames(self, n=1):
        """Reads and throws away n frames """
        w, h = self.size
        for i in range(n):
            self.proc.stdout.read(self.depth*w*h)
            self.proc.stdout.flush()
        self.pos += n


    def read_frame(self):
        w, h = self.size
        nbytes= self.depth*w*h
        try:
            # Normally, the reader should not read after the last frame.
            # if it does, raise an error.
            s = self.proc.stdout.read(nbytes)
            assert len(s) == nbytes
            result = np.fromstring(s,
                             dtype='uint8').reshape((h, w, len(s)//(w*h)))
            #self.proc.stdout.flush()
            
        except IOError:
            
            self.proc.terminate()
            serr = self.proc.stderr.read()
            print( "error: string: %s, stderr: %s" % (s, serr))
            raise IOError

        self.lastread = result

        return result

    def get_frame(self, t):
        """ Read a file video frame at time t.
        
        Note for coders: getting an arbitrary frame in the video with
        ffmpeg can be painfully slow if some decoding has to be done.
        This function tries to avoid fectching arbitrary frames whenever
        possible, by moving between adjacent frames.
            """
        if t < 0:
            t = 0
        elif t > self.duration:
            t = self.duration

        pos = int(np.round(self.fps*t))+1
        if pos > self.nframes+1:
            raise ValueError("Video file %s has only %d frames but frame"
                              " #%d asked"%(self.filename, self.nframes, pos))
        


        if pos == self.pos:
            return self.lastread
        else:
            if(pos < self.pos) or (pos > self.pos+100):
                self.initialize(t)
            else:
                self.skip_frames(pos-self.pos-1)
            result = self.read_frame()
            self.pos = pos
            return result
    
    def close(self):
        if self.proc is not None:
            self.proc.terminate()
            self.proc.stdout.close()
            self.proc.stderr.close()
            del self.proc
    
    def __del__(self):
        self.close()
        del self.lastread
    


def ffmpeg_read_image(filename, with_mask=True):
    """ Read one image from a file.
    
    Wraps FFMPEG_Videoreader to read just one image. Returns an
    ImageClip.
    
    Parameters
    -----------
    
    filename
      Name of the image file. Can be of any format supported by ffmpeg.
    
    with_mask
      If the image has a transparency layer, ``with_mask=true`` will save
      this layer as the mask of the returned ImageClip
    
    """
    if with_mask:
        pix_fmt = 'rgba'
    else:
        pix_fmt = "rgb24"
    reader = FFMPEG_VideoReader(filename, pix_fmt=pix_fmt)
    im = reader.lastread
    del reader
    return im
