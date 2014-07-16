
import numpy as np
from moviepy.audio.io.ffmpeg_audiowriter import ffmpeg_audiowrite
from moviepy.decorators import requires_duration
from moviepy.tools import deprecated_version_of

from moviepy.Clip import Clip


class AudioClip(Clip):
    """ Base class for audio clips.
    
    See ``SoundClip`` and ``CompositeSoundClip`` for usable classes.
    
    An AudioClip is a Clip with a ``get_frame``  attribute of
    the form `` t -> [ f_t ]`` for mono sound and
    ``t-> [ f1_t, f2_t ]`` for stereo sound (the arrays are Numpy arrays).
    The `f_t` are floats between -1 and 1. These bounds can be
    trespassed wihtout problems (the program will put the
    sound back into the bounds at conversion time, without much impact). 
    
    Parameters
    -----------
    
    get_frame
      A function `t-> frame at time t`. The frame does not mean much
      for a sound, it is just a float. What 'makes' the sound are
      the variations of that float in the time.
        
    nchannels
      Number of channels (one or two for mono or stereo).
    
    Examples
    ---------
    
    >>> # Plays the note A (a sine wave of frequency 404HZ)
    >>> import numpy as np
    >>> gf = lambda t : 2*[ np.sin(404 * 2 * np.pi * t) ]
    >>> clip = AudioClip().set_get_frame(gf)
    >>> clip.set_duration(5).preview()
                     
    """
    
    def __init__(self, get_frame = None):
        Clip.__init__(self)
        if get_frame:
            self.get_frame = get_frame
            frame0 = self.get_frame(0)
            if hasattr(frame0, '__iter__'):
                self.nchannels = len(list(frame0))
            else:
                self.nchannels = 1

    @requires_duration
    def to_soundarray(self,tt=None,fps=None, nbytes=2):
        """
        Transforms the sound into an array that can be played by pygame
        or written in a wav file. See ``AudioClip.preview``.
        
        Parameters
        ------------
        
        fps
          Frame rate of the sound for the conversion.
          44100 for top quality.
        
        nbytes
          Number of bytes to encode the sound: 1 for 8bit sound,
          2 for 16bit, 4 for 32bit sound.
          
        """
        if tt is None:
            tt = np.arange(0,self.duration, 1.0/fps)

        #print tt.max() - tt.min(), tt.min(), tt.max()
        
        snd_array = self.get_frame(tt)
        snd_array = np.maximum(-0.99,
                       np.minimum(0.99,snd_array))
        inttype = {1:'int8',2:'int16', 4:'int32'}[nbytes]
        return (2**(8*nbytes-1)*snd_array).astype(inttype)
    
    
    
    @requires_duration
    def write_audiofile(self,filename, fps=44100, nbytes=2,
                     buffersize=2000, codec='libvorbis',
                     bitrate=None, write_logfile=False, verbose=True):
        """ Writes an audio file from the AudioClip.


        Parameters
        -----------

        filename
          Name of the output file

        fps
          Frames per second

        nbyte
          Sample width (set to 2 for 16-bit sound, 4 for 32-bit sound)

        codec
          Which audio codec should be used. Examples are 'libmp3lame'
          for '.mp3', 'libvorbis' for 'ogg', 'libfdk_aac':'m4a',
          'pcm_s16le' for 16-bit wav and 'pcm_s32le' for 32-bit wav.

        bitrate
          Audio bitrate, given as a string like '50k', '500k', '3000k'.
          Will determine the size and quality of the output file.
          Note that it mainly an indicative goal, the bitrate won't
          necessarily be the this in the output file.

        write_logfile
          If true, produces a detailed logfile named filename + '.log'
          when writing the file

        verbose
          If True, displays informations

        """
                         
        return ffmpeg_audiowrite(self, filename, fps, nbytes, buffersize,
                      codec=codec, bitrate=bitrate, write_logfile=write_logfile,
                      verbose=verbose)

###
#
# The to_audiofile method is replaced by the more explicit write_audiofile.
AudioClip.to_audiofile = deprecated_version_of(AudioClip.write_audiofile,
                                               'to_audiofile')
###

class AudioArrayClip(AudioClip):
    """
    
    An audio clip made from a sound array.
    
    Parameters
    -----------
    
    array
      A Numpy array representing the sound, of size Nx1 for mono,
      Nx2 for stereo.
       
    fps
      Frames per second : speed at which the sound is supposed to be
      played.
    
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
        self.nchannels = len(list(self.get_frame(0)))
        
        
class CompositeAudioClip(AudioClip):

    """ Clip made by composing several AudioClips.
    
    An audio clip made by putting together several audio clips.
    
    Parameters
    ------------
    
    clips
      List of audio clips, which may start playing at different times or
      together. If all have their ``duration`` attribute set, the
      duration of the composite clip is computed automatically.
    
    """

    def __init__(self, clips):

        Clip.__init__(self)
        self.clips = clips
        
        ends = [c.end for c in self.clips]
        self.nchannels = max([c.nchannels for c in self.clips])
        if not any([(e is None) for e in ends]):
            self.duration = max(ends)
            self.end = max(ends)

        def get_frame(t):
            
            played_parts = [c.is_playing(t) for c in self.clips]
            
            sounds= [c.get_frame(t - c.start)*np.array([part]).T
                     for c,part in zip(self.clips, played_parts)
                     if (part is not False) ]
                     
            if isinstance(t,np.ndarray):
                zero = np.zeros((len(t),self.nchannels))
                
            else:
                zero = np.zeros(self.nchannels)
                
            return zero + sum(sounds)

        self.get_frame = get_frame

def concatenate_audio(clips):
    durations = [c.duration for c in clips]
    tt = np.cumsum([0]+durations) # start times, and end time.
    newclips= [c.set_start(t) for c,t in zip(clips, tt)]
    return CompositeAudioClip(newclips).set_duration(tt[-1])
