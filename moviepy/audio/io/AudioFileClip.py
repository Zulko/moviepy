from __future__ import division

import wave
import numpy as np

from moviepy.Clip import Clip
from moviepy.audio.AudioClip import AudioClip
from moviepy.audio.io.readers import FFMPEG_AudioReader

class AudioFileClip(AudioClip):

    """
    
    An audio clip read from a sound file, or an array.
    The whole file is not loaded in memory. Instead, only a portion is
    read and stored in memory. this portion includes frames before
    and after the last frames read, so that it is fast to read the sound
    backward and forward.
    
    
    :param snd: Either a soundfile or an array representing a sound. If
        the soundfile is not a .wav, it will be converted to .wav first,
        using the ``fps`` and ``bitrate`` arguments. 
    
    :param buffersize: Size to load in memory (in number of frames)
    :param temp_wav: name for the temporary wav file in case conversion
        is required. If not provided, the default will be filename.wav
        with some prefix. If the temp_wav already exists it will not
        be rewritten.
        
    :ivar nbytes: Number of bits per frame of the original audio file
        (the more the better).
    :ivar fps, buffersize: see above.
    
    >>> snd = SoundClip("song.wav")
    >>> snd = SoundClip("song.mp3", fps = 44100, bitrate=3000)
    >>> snd = SoundClip(mySoundArray,fps=44100) # from a numeric array
    
    """

    def __init__(self, filename, buffersize=200000, nbytes=2, fps=44100):
        

        Clip.__init__(self)
            
        self.filename = filename
        self.reader = FFMPEG_AudioReader(filename,fps=fps,nbytes=nbytes,
                                         bufsize=buffersize+100)
        self.fps = fps
        self.duration = self.reader.duration
        self.end = self.duration
        
        self.nframes = self.reader.nframes
        self.buffersize= buffersize
        self.buffer= None
        self._fstart_buffer = 1
        self._buffer_around(1)
        
        def gf(t):
            bufsize = self.buffersize
            if isinstance(t,np.ndarray):
                # lazy implementation, but should not cause problems in
                # 99.99 %  of the cases
                result = np.zeros((len(t),2))
                in_time = (t>=0) & (t < self.duration)
                inds = (self.fps*t+1).astype(int)[in_time]
                f_tmin, f_tmax = inds.min(), inds.max()
                
                if not (0 <= (f_tmin - self._fstart_buffer) < len(self.buffer)):
                    self._buffer_around(f_tmin)
                elif not (0 <= (f_tmax - self._fstart_buffer) < len(self.buffer)):
                    self._buffer_around(f_tmax)
                    
                try:
                    result[in_time] = self.buffer[inds - self._fstart_buffer]
                    return result
                except:
                    print ("Error: wrong indices in video buffer. Maybe"+
                           " buffer too small.")
                    raise
            else:
                ind = int(self.fps*t)#+1
                if ind<1 or ind> self.nframes: # out of time: return 0
                    return np.zeros(self.nchannels)
                    
                if not (0 <= (ind - self._fstart_buffer) <len(self.buffer)):
                    # out of the buffer: recenter the buffer
                    self._buffer_around(ind)
                    
                # read the frame in the buffer
                return self.buffer[ind - self._fstart_buffer]

        self.get_frame = gf

    @property
    def nchannels(self):
        """
        returns the number of channels of the reader
        (1: mono, 2: stereo)
        """
        return self.reader.nchannels

    def _buffer_around(self,framenumber):
        """
        fill the buffer with frames, centered on ``framenumber``
        if possible
        """
                # start frame for the buffer
        fbuffer = framenumber - self.buffersize//2
        fbuffer = max(1, fbuffer)
        
        
        if (self.buffer!=None):
            current_f_end  =self._fstart_buffer + self.buffersize-1
            if (fbuffer < current_f_end  < fbuffer+ self.buffersize):
                # We already have one bit of what must be read
                conserved = current_f_end - fbuffer+1
                chunksize = self.buffersize-conserved
                array = self.reader.read_chunk(chunksize)
                self.buffer = np.vstack([self.buffer[-conserved:], array])
            else:
                self.reader.seek(fbuffer)
                self.buffer =  self.reader.read_chunk(self.buffersize)
        else:
            self.reader.seek(fbuffer)
            self.buffer =  self.reader.read_chunk(self.buffersize)
        
        self._fstart_buffer = fbuffer
    
    def coreader(self):
        """ Returns a copy of the AudioFileClip, i.e. a new entrance point
            to the audio file. Use copy when you have different clips
            watching the audio file at different times. """
        return AudioFileClip(self.filename,self.buffersize)
