import time
import os
import sys
import wave
from copy import copy

import numpy as np
from moviepy.audio.io.ffmpeg_audiowriter import ffmpeg_audiowrite
from moviepy.decorators import  requires_duration

from moviepy.Clip import Clip


# optimize range in function of Python's version
if sys.version_info < (3,):
    range = xrange


class AudioClip(Clip):

    """
    
    Base class for audio clips. See ``SoundClip`` and ``CompositeSoundClip``
    for usable classes.
    An audio clip is a special clip with a ``get_frame``  attribute of
    the form ` t -> [ f_t ]` for mono sound and `t -> [ f1_t, f2_t ]`
    for stereo sound.  The `f_t` are floats between -1 and 1. These
    bounds can be trespassed wihtout problems (the program will put the
    sound back into the bounds at conversion time, without much impact). 
    
    Example :
    
    >>> # Plays the note A (a sine wave of frequency 404HZ)
    >>> import numpy as np
    >>> gf = lambda t : 2*[ np.sin(404 * 2 * np.pi * t) ]
    >>> clip = AudioClip().set_get_frame(gf)
    >>> clip.set_duration(5).preview()
    
    
    :ivar get_frame: A function `t-> frame at time t`. The frame does not
        mean much for a sound, it is just a float. What 'makes' the sound
        are the variations of that float in the time.
        
    :ivar nchannels: Number of channels (one or two for mono or stereo).
                     
    """
    
    def __init__(self):
        Clip.__init__(self)

    @requires_duration
    def to_soundarray(self,tt=None,fps=None, nbytes=2):
        """
        Transforms the sound into an array that can be played by pygame
        or written in a wav file. See ``AudioClip.preview``.
        
        :param fps: frame rate of the sound. 44100 gives top quality.
        
        :param nbytes: number of bytes to encode the sound: 1 for 8bit
            sound, 2 for 16bit, 4 for 32bit sound.
        """
        if tt is None:
            tt = np.arange(0,self.duration, 1.0/fps)
        
        snd_array = self.get_frame(tt)
        snd_array = np.maximum(-0.999, np.minimum(0.999,snd_array))
        inttype = {1:'int8',2:'int16',4:'int32'}[nbytes]
        return (2**(8*nbytes-1)*snd_array).astype(inttype)

    @property
    def nchannels(self):
        return len(list(self.get_frame(0)))
    
    
    @requires_duration
    def to_audiofile(self,filename, fps=44100, nbytes=2,
                     buffersize=5000, codec='libvorbis',
                     bitrate=None, verbose=True):
                         
        return ffmpeg_audiowrite(self,filename, fps, nbytes, buffersize,
                      codec, bitrate, verbose)

try:
    
    # Add method preview (only if pygame installed)
    from moviepy.audio.io.preview import preview
    AudioClip.preview = preview
    
except:
    pass
        

class AudioArrayClip(AudioClip):
    """
    
    An audio clip made from a sound array.
    
    :param fps: Frames per rate
    
    """
    
    def __init__(self, array, fps):
        
        Clip.__init__(self)
        self.array = array
        self.fps = fps
        self.duration = 1.0 * len(array) / fps
        
        
        def get_frame(t):
            """ complicated, but must be able to handle the case where t
            is a list of the form sin(t) """
            
            if isinstance(t, np.ndarray):
                array_inds = (self.fps*t).astype(int)
                in_array = (array_inds>0) & (array_inds < len(self.array))
                result = np.zeros((len(t),2))
                result[in_array] = self.array[array_inds[in_array]]
                return result
            else:
                i = int(self.fps * t)
                if i < 0 or i >= len(self.array):
                    return 0*self.array[0]
                else:
                    return self.array[i]

        self.get_frame = get_frame
        
        
class CompositeAudioClip(AudioClip):

    """
    
    An audio clip made by putting together several audio clips.
    
    :param clips: a list of audio clips, which may start playing at
        different times or together. If all have their ``duration``
        attribute set, the duration of the composite clip is computed
        automatically.
    
    """

    def __init__(self, clips):

        Clip.__init__(self)
        self.clips = clips
        
        ends = [c.end for c in self.clips]
        if not any([(e is None) for e in ends]):
            self.duration = max(ends)

        def get_frame(t):
            
            sounds= [c.get_frame(t - c.start)
                     for c in clips if c.is_playing(t)]
                     
            if isinstance(t,np.ndarray):
                zero = np.zeros((len(t),2))
                
            else:
                zero = np.zeros(2)
                
            return zero + sum(sounds)

        self.get_frame = get_frame
