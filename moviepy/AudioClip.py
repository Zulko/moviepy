import time
import os
from copy import copy, deepcopy
import shutil

import numpy as np
from scipy.io import wavfile

import pygame as pg
import ffmpeg

from Clip import Clip, requires_duration


class AudioClip(Clip):

    """
    
    Base class for audio clips. See ``SoundClip`` and ``CompositeSoundClip``
    for usable classes. 
    
    :ivar get_frame: A function `t-> frame at time t`. the frame does not
        mean much for a sound, it is just an integer.
        
    :ivar nchannels: Number of channels (one or two for mono or stereo)
                     of the sound.
         
    :ivar nbits: Number of bits per frame (the more the better).
    """

    def __init__(self):
        Clip.__init__(self)

    @requires_duration
    def toSoundClip(self, fps=24000):
        """ Transforms the clip into a soundclip by (audio clip with a
            precomputed sound array """

        tt = np.linspace(0, self.duration, self.duration * fps)[:-1]
        arr = np.array(map(self.get_frame, tt)).astype('int16')
        return SoundClip(arr, fps)

    @requires_duration
    def preview(self, fps=22050, sleep=True):
        """ Plays the sound clip with pygame. If ``sleep=True`` the
            program is freezed while the sound is playing (necessary
            when the sound is playing alone without video)."""
        pg.mixer.quit()
        array = self.toSoundClip(fps).array
        pg.mixer.init(fps, -8 * self.nbits, self.nchannels, 4096)
        snd = pg.sndarray.make_sound(array)
        snd.play()
        if sleep:
            time.sleep(self.duration)

    @requires_duration
    def to_soundfile(self, filename=None, fps=22050):
        """ Writes the soundclip to a .wav file """
        array = self.toSoundClip(fps).array
        wavfile.write(filename, fps, array)

    def volumex(self, factor):
        """ Returns an audioclip playing the same sound but with a volume
            multiplied by the ``factor``. """
        return self.fl(lambda gf, t: factor * gf(t))

    def fadein(self, duration):
        """ Return a sound clip that is first mute, then the sound arrives
            progressively over ``duration`` seconds. """
        fading = lambda gf, t: min(1.0 * t / duration, 1) * gf(t)
        return self.fl(fading)

    @requires_duration
    def fadeout(self, duration):
        """ Return a sound clip where the sound fades out progressively
            over ``duration`` seconds at the end of the clip. """
        fading = lambda gf, t: min(
            1.0 * (self.duration - t) / duration, 1) * gf(t)
        return self.fl(fading)

    @property
    def nchannels(self):
        return len(list(self.get_frame(0)))

    @property
    def nbits(self):
        return self.get_frame(0).itemsize


class SoundClip(AudioClip):

    """
    
    An audio clip read from a sound file, or an array.
    
    :param snd: Either a soundfile or an array representing a sound. If
        the soundfile is not a .wav, it will be converted to .wav first,
        using the ``fps`` and ``bitrate`` arguments. 
    
    :param fps: If ``snd`` is an  array, this parameter is required.
    :param bitrate: If ``snd`` is not a .wav, this prameter is required
        for the conversion.
    
    >>> snd = SoundClip("song.wav")
    >>> snd = SoundClip("song.mp3", fps = 44100, bitrate=3000)
    >>> snd = SoundClip(mySoundArray,fps=44100) # from a numeric array
    
    """

    def __init__(self, snd, fps=None, bitrate=3000):

        Clip.__init__(self)

        if isinstance(snd, str):
            if not snd.endswith('.wav'):
                temp = 'temp.wav'
                ffmpeg.extract_sound(snd, temp, fps, bitrate)
                fps, arr = wavfile.read(temp)
                # os.remove(temp)
            else:
                fps, arr = wavfile.read(snd)

            self.array = arr
            self.fps = fps
        else:
            self.array = snd
            self.fps = fps

        self.duration = 1.0 * len(self.array) / self.fps

        def gf(t):
            i = int(self.fps * t)
            if i < 0 or i >= len(self.array):
                return 0
            else:
                return self.array[i]

        self.get_frame = gf


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
        self.compute_duration()

        def gf(t):
            return sum([0*self.clips[0].get_frame(0)]+
                        [c.get_frame(t - c.start)
                                 for c in self.playing_clips(t)])

        self.get_frame = gf

    def compute_duration(self):
        ends = [c.end for c in self.clips]
        if not any([(e is None) for e in ends]):
            self.duration = max(ends)

    def playing_clips(self, t=0):
        return [c for c in self.clips if c.is_playing(t)]
