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
        infos = ffmpeg_parse_infos(filename, print_infos)
        self.fps = infos['video_fps']
        self.size = infos['video_size']
        self.duration = infos['video_duration']
        self.ffmpeg_duration = infos['duration']
        self.nframes = infos['video_nframes']

        self.infos = infos

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

        s = self.proc.stdout.read(nbytes)
        if len(s) != nbytes:

            print( "Warning: in file %s, "%(self.filename)+
                   "%d bytes wanted but %d bytes read,"%(nbytes, len(s))+
                   "at frame %d/%d, at time %.02f/%.02f sec. "%(
                    self.pos,self.nframes,
                    1.0*self.pos/self.fps,
                    self.duration)+
                   "Using the last valid frame instead.")
            result = self.lastread

        else:

            result = np.fromstring(s, dtype='uint8').\
                         reshape((h, w, len(s)//(w*h)))
            self.lastread = result

        return result

    def get_frame(self, t):
        """ Read a file video frame at time t.
        
        Note for coders: getting an arbitrary frame in the video with
        ffmpeg can be painfully slow if some decoding has to be done.
        This function tries to avoid fectching arbitrary frames
        whenever possible, by moving between adjacent frames.
        """

        # these definitely need to be rechecked sometime. Seems to work.
        #pos = min( self.nframes, int(np.round(self.fps*t))+1 )
        #if pos > self.nframes:
        #    raise ValueError(("Video file %s has only %d frames but"
        #                     " frame #%d asked")%(
        #                        self.filename, self.nframes, pos))
        
        pos = int(self.fps*t)+1

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

def ffmpeg_parse_infos(filename, print_infos=False):
    """Get file infos using ffmpeg.

    Returns a dictionnary with the fields:
    "video_found", "video_fps", "duration", "video_nframes",
    "video_duration"
    "audio_found", "audio_fps"

    "video_duration" is slightly smaller than "duration" to avoid
    fetching the uncomplete frames at the end, which raises an error.

    """
    

    # open the file in a pipe, provoke an error, read output
    is_GIF = filename.endswith('.gif')
    cmd = [FFMPEG_BINARY, "-i", filename]
    if is_GIF:
        cmd += ["-f", "null", "/dev/null"]
    proc = sp.Popen(cmd,
            bufsize=10**5,
            stdout=sp.PIPE,
            stderr=sp.PIPE)

    proc.stdout.readline()
    proc.terminate()
    infos = proc.stderr.read().decode('utf8')
    del proc

    if print_infos:
        # print the whole info text returned by FFMPEG
        print( infos )


    lines = infos.splitlines()
    if "No such file or directory" in lines[-1]:
        raise IOError("%s not found ! Wrong path ?"%filename)
    
    result = dict()
    

    # get duration (in seconds)
    try:
        keyword = ('frame=' if is_GIF else 'Duration: ')
        line = [l for l in lines if keyword in l][0]
        match = re.search("[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9]", line)
        hms = map(float, line[match.start()+1:match.end()].split(':'))
        result['duration'] = cvsecs(*hms)
    except:
        raise IOError("Error reading duration in file %s,"%(filename)+
                      "Text parsed: %s"%infos)

    # get the output line that speaks about video
    lines_video = [l for l in lines if ' Video: ' in l]
    
    result['video_found'] = ( lines_video != [] )
    
    if result['video_found']:
        
        line = lines_video[0]

        # get the size, of the form 460x320 (w x h)
        match = re.search(" [0-9]*x[0-9]*(,| )", line)
        s = list(map(int, line[match.start():match.end()-1].split('x')))
        result['video_size'] = s


        # get the frame rate
        try:
            match = re.search("( [0-9]*.| )[0-9]* tbr", line)
            result['video_fps'] = float(line[match.start():match.end()].split(' ')[1])
        except:
            match = re.search("( [0-9]*.| )[0-9]* fps", line)
            result['video_fps'] = float(line[match.start():match.end()].split(' ')[1])

        result['video_nframes'] = int(result['duration']*result['video_fps'])+1

        result['video_duration'] = result['duration']
        # We could have also recomputed the duration from the number
        # of frames, as follows:
        # >>> result['video_duration'] = result['video_nframes'] / result['video_fps']


    lines_audio = [l for l in lines if ' Audio: ' in l]
    
    result['audio_found'] = lines_audio != []
    
    if result['audio_found']:
        line = lines_audio[0]
        try:
            match = re.search(" [0-9]* Hz", line)
            result['audio_fps'] = int(line[match.start()+1:match.end()])
        except:
            result['audio_fps'] = 'unknown'

    return result
