import subprocess as sp
import warnings

import numpy as np
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos
from moviepy.config import get_setting
from moviepy.compat import PY3, DEVNULL
import os


class FFMPEG_AudioReader:
    """
    A class to read the audio in either video files or audio files
    using ffmpeg. ffmpeg will read any audio and transform them into
    raw data.

    Parameters
    ------------

    filename
      Name of any video or audio file, like ``video.mp4`` or
      ``sound.wav`` etc.

    buffersize
      The size of the buffer to use. Should be bigger than the buffer
      used by ``to_audiofile``

    print_infos
      Print the ffmpeg infos on the file being read (for debugging)

    fps
      Desired frames per second in the decoded signal that will be
      received from ffmpeg

    nbytes
      Desired number of bytes (1,2,4) in the signal that will be
      received from ffmpeg

    """

    def __init__(self, filename, buffersize, print_infos=False,
                 fps=44100, nbytes=2, nchannels=2):

        self.filename = filename
        self.nbytes = nbytes
        self.fps = fps
        self.f = 's%dle'%(8*nbytes)
        self.acodec = 'pcm_s%dle'%(8*nbytes)
        self.nchannels = nchannels
        infos = ffmpeg_parse_infos(filename)
        self.duration = infos['duration']
        if 'video_duration' in infos:
            self.duration = infos['video_duration']
        else:
            self.duration = infos['duration']
        self.infos = infos
        self.proc = None

        self.nframes = int(self.fps * self.duration)
        self.buffersize= min( self.nframes+1, buffersize )
        self.buffer= None
        self.buffer_startframe = 1
        self.initialize()
        self.buffer_around(1)



    def initialize(self, starttime = 0):
        """ Opens the file, creates the pipe. """

        self.close_proc() # if any

        if starttime !=0 :
            offset = min(1,starttime)
            i_arg = ["-ss", "%.05f"%(starttime-offset),
                    '-i', self.filename, '-vn',
                    "-ss", "%.05f"%offset]
        else:
            i_arg = [ '-i', self.filename,  '-vn']


        cmd = ([get_setting("FFMPEG_BINARY")] + i_arg +
               [ '-loglevel', 'error',
                 '-f', self.f,
                '-acodec', self.acodec,
                '-ar', "%d"%self.fps,
                '-ac', '%d'%self.nchannels, '-'])

        popen_params = {"bufsize": self.buffersize,
                        "stdout": sp.PIPE,
                        "stderr": sp.PIPE,
                        "stdin": DEVNULL}

        if os.name == "nt":
            popen_params["creationflags"] = 0x08000000

        self.proc = sp.Popen( cmd, **popen_params)

        self.pos = np.round(self.fps*starttime)



    def skip_chunk(self,chunksize):
        s = self.proc.stdout.read(self.nchannels*chunksize*self.nbytes)
        self.proc.stdout.flush()
        self.pos = self.pos+chunksize



    def read_chunk(self,chunksize):
        # chunksize is not being autoconverted from float to int
        chunksize = int(round(chunksize))
        L = self.nchannels*chunksize*self.nbytes
        s = self.proc.stdout.read(L)
        dt = {1: 'int8',2:'int16',4:'int32'}[self.nbytes]
        if hasattr(np, 'frombuffer'):
            result = np.frombuffer(s, dtype=dt)
        else:
            result = np.fromstring(s, dtype=dt)
        result = (1.0*result / 2**(8*self.nbytes-1)).\
                                 reshape((int(len(result)/self.nchannels),
                                          self.nchannels))
        #self.proc.stdout.flush()
        self.pos = self.pos+chunksize
        return result



    def seek(self,pos):
        """
        Reads a frame at time t. Note for coders: getting an arbitrary
        frame in the video with ffmpeg can be painfully slow if some
        decoding has to be done. This function tries to avoid fectching
        arbitrary frames whenever possible, by moving between adjacent
        frames.
        """
        if (pos < self.pos) or (pos> (self.pos+1000000)):
            t = 1.0*pos/self.fps
            self.initialize(t)
        elif pos > self.pos:
            #print pos
            self.skip_chunk(pos-self.pos)
        # last case standing: pos = current pos
        self.pos = pos



    def close_proc(self):
        if hasattr(self, 'proc') and self.proc is not None:
            self.proc.terminate()
            for std in [ self.proc.stdout,
                         self.proc.stderr]:
                std.close()
            self.proc = None

    def get_frame(self, tt):

        buffersize = self.buffersize
        if isinstance(tt,np.ndarray):
            # lazy implementation, but should not cause problems in
            # 99.99 %  of the cases


            # elements of t that are actually in the range of the
            # audio file.
            in_time = (tt>=0) & (tt < self.duration)

        # Check that the requested time is in the valid range
            if not in_time.any():
                raise IOError("Error in file %s, "%(self.filename)+
                       "Accessing time t=%.02f-%.02f seconds, "%(tt[0], tt[-1])+
                       "with clip duration=%d seconds, "%self.duration)

            # The np.round in the next line is super-important.
            # Removing it results in artifacts in the noise.
            frames = np.round((self.fps*tt)).astype(int)[in_time]
            fr_min, fr_max = frames.min(), frames.max()

            if not (0 <=
                     (fr_min - self.buffer_startframe)
                          < len(self.buffer)):
                self.buffer_around(fr_min)
            elif not (0 <=
                        (fr_max - self.buffer_startframe)
                             < len(self.buffer)):
                self.buffer_around(fr_max)

            try:
                result = np.zeros((len(tt),self.nchannels))
                indices = frames - self.buffer_startframe
                if len(self.buffer) < self.buffersize // 2:
                    indices = indices - (self.buffersize // 2 - len(self.buffer) + 1)
                result[in_time] = self.buffer[indices]
                return result

            except IndexError as error:
                warnings.warn("Error in file %s, "%(self.filename)+
                       "At time t=%.02f-%.02f seconds, "%(tt[0], tt[-1])+
                       "indices wanted: %d-%d, "%(indices.min(), indices.max())+
                       "but len(buffer)=%d\n"%(len(self.buffer))+ str(error),
                   UserWarning)

                # repeat the last frame instead
                indices[indices>=len(self.buffer)] = len(self.buffer) -1
                result[in_time] = self.buffer[indices]
                return result

        else:

            ind = int(self.fps*tt)
            if ind<0 or ind> self.nframes: # out of time: return 0
                return np.zeros(self.nchannels)

            if not (0 <= (ind - self.buffer_startframe) <len(self.buffer)):
                # out of the buffer: recenter the buffer
                self.buffer_around(ind)

            # read the frame in the buffer
            return self.buffer[ind - self.buffer_startframe]


    def buffer_around(self,framenumber):
        """
        Fills the buffer with frames, centered on ``framenumber``
        if possible
        """

        # start-frame for the buffer
        new_bufferstart = max(0,  framenumber - self.buffersize // 2)


        if (self.buffer is not None):
            current_f_end  = self.buffer_startframe + self.buffersize
            if (new_bufferstart <
                        current_f_end  <
                               new_bufferstart + self.buffersize):
                # We already have one bit of what must be read
                conserved = current_f_end - new_bufferstart + 1
                chunksize = self.buffersize-conserved
                array = self.read_chunk(chunksize)
                self.buffer = np.vstack([self.buffer[-conserved:], array])
            else:
                self.seek(new_bufferstart)
                self.buffer =  self.read_chunk(self.buffersize)
        else:
            self.seek(new_bufferstart)
            self.buffer =  self.read_chunk(self.buffersize)

        self.buffer_startframe = new_bufferstart


    def __del__(self):
        # If the garbage collector comes, make sure the subprocess is terminated.
        self.close_proc()
