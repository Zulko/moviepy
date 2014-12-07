from __future__ import division

import numpy as np

from moviepy.audio.AudioClip import AudioClip
from moviepy.audio.io.readers import FFMPEG_AudioReader

class AudioFileClip(AudioClip):

    """
    An audio clip read from a sound file, or an array.
    The whole file is not loaded in memory. Instead, only a portion is
    read and stored in memory. this portion includes frames before
    and after the last frames read, so that it is fast to read the sound
    backward and forward.
    
    Parameters
    ------------
    
    snd
      Either a soundfile name (of any extension supported by ffmpeg)
      or an array representing a sound. If the soundfile is not a .wav,
      it will be converted to .wav first, using the ``fps`` and
      ``bitrate`` arguments. 
    
    buffersize:
      Size to load in memory (in number of frames)
    
    temp_wav:
      Name for the temporary wav file in case conversion is required.
      If not provided, the default will be filename.wav with some prefix.
      If the temp_wav already exists it will not be rewritten.
        
        
    Attributes
    ------------
    
    nbytes
      Number of bits per frame of the original audio file.
      
    fps
      Number of frames per second in the audio file
      
    buffersize
      See Parameters.
      
    Examples
    ----------
    
    >>> snd = SoundClip("song.wav")
    >>> snd = SoundClip("song.mp3", fps = 44100, bitrate=3000)
    >>> snd = SoundClip(mySoundArray,fps=44100) # from a numeric array
    
    """

    def __init__(self, filename, buffersize=200000, nbytes=2, fps=44100):
        

        AudioClip.__init__(self)
            
        self.filename = filename
        reader = FFMPEG_AudioReader(filename,fps=fps,nbytes=nbytes,
                                         buffersize=buffersize)
        
        self.reader = reader
        self.fps = fps
        self.duration = reader.duration
        self.end = reader.duration
        
        
        self.make_frame =  lambda t: reader.get_frame(t)
        self.nchannels = reader.nchannels
    
    
    def coreader(self):
        """ Returns a copy of the AudioFileClip, i.e. a new entrance point
            to the audio file. Use copy when you have different clips
            watching the audio file at different times. """
        return AudioFileClip(self.filename,self.buffersize)
