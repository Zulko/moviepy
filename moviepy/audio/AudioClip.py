"""Implements AudioClip (base class for audio clips) and its main subclasses:

- Audio clips: AudioClip, AudioFileClip, AudioArrayClip
- Composition: CompositeAudioClip
"""

import numbers
import os

import numpy as np
import proglog

from moviepy.audio.io.ffmpeg_audiowriter import ffmpeg_audiowrite
from moviepy.Clip import Clip
from moviepy.decorators import convert_path_to_string, requires_duration
from moviepy.tools import extensions_dict


class AudioClip(Clip):
    """Base class for audio clips.

    See ``AudioFileClip`` and ``CompositeAudioClip`` for usable classes.

    An AudioClip is a Clip with a ``make_frame``  attribute of
    the form `` t -> [ f_t ]`` for mono sound and
    ``t-> [ f1_t, f2_t ]`` for stereo sound (the arrays are Numpy arrays).
    The `f_t` are floats between -1 and 1. These bounds can be
    trespassed without problems (the program will put the
    sound back into the bounds at conversion time, without much impact).

    Parameters
    ----------

    make_frame
      A function `t-> frame at time t`. The frame does not mean much
      for a sound, it is just a float. What 'makes' the sound are
      the variations of that float in the time.

    duration
      Duration of the clip (in seconds). Some clips are infinite, in
      this case their duration will be ``None``.

    nchannels
      Number of channels (one or two for mono or stereo).

    Examples
    --------

    >>> # Plays the note A in mono (a sine wave of frequency 440 Hz)
    >>> import numpy as np
    >>> make_frame = lambda t: np.sin(440 * 2 * np.pi * t)
    >>> clip = AudioClip(make_frame, duration=5, fps=44100)
    >>> clip.preview()

    >>> # Plays the note A in stereo (two sine waves of frequencies 440 and 880 Hz)
    >>> make_frame = lambda t: np.array([
    ...     np.sin(440 * 2 * np.pi * t),
    ...     np.sin(880 * 2 * np.pi * t)
    ... ]).T.copy(order="C")
    >>> clip = AudioClip(make_frame, duration=3, fps=44100)
    >>> clip.preview()

    """

    def __init__(self, make_frame=None, duration=None, fps=None):
        super().__init__()

        if fps is not None:
            self.fps = fps

        if make_frame is not None:
            self.make_frame = make_frame
            frame0 = self.get_frame(0)
            if hasattr(frame0, "__iter__"):
                self.nchannels = len(list(frame0))
            else:
                self.nchannels = 1
        if duration is not None:
            self.duration = duration
            self.end = duration

    @requires_duration
    def iter_chunks(
        self,
        chunksize=None,
        chunk_duration=None,
        fps=None,
        quantize=False,
        nbytes=2,
        logger=None,
    ):
        """Iterator that returns the whole sound array of the clip by chunks"""
        if fps is None:
            fps = self.fps
        logger = proglog.default_bar_logger(logger)
        if chunk_duration is not None:
            chunksize = int(chunk_duration * fps)

        total_size = int(fps * self.duration)

        nchunks = total_size // chunksize + 1

        positions = np.linspace(0, total_size, nchunks + 1, endpoint=True, dtype=int)

        for i in logger.iter_bar(chunk=list(range(nchunks))):
            size = positions[i + 1] - positions[i]
            assert size <= chunksize
            timings = (1.0 / fps) * np.arange(positions[i], positions[i + 1])
            yield self.to_soundarray(
                timings, nbytes=nbytes, quantize=quantize, fps=fps, buffersize=chunksize
            )

    @requires_duration
    def to_soundarray(
        self, tt=None, fps=None, quantize=False, nbytes=2, buffersize=50000
    ):
        """
        Transforms the sound into an array that can be played by pygame
        or written in a wav file. See ``AudioClip.preview``.

        Parameters
        ----------

        fps
          Frame rate of the sound for the conversion.
          44100 for top quality.

        nbytes
          Number of bytes to encode the sound: 1 for 8bit sound,
          2 for 16bit, 4 for 32bit sound.

        """
        if tt is None:
            if fps is None:
                fps = self.fps

            max_duration = 1 * buffersize / fps
            if self.duration > max_duration:
                stacker = np.vstack if self.nchannels == 2 else np.hstack
                return stacker(
                    tuple(
                        self.iter_chunks(
                            fps=fps, quantize=quantize, nbytes=2, chunksize=buffersize
                        )
                    )
                )
            else:
                tt = np.arange(0, self.duration, 1.0 / fps)
        """
        elif len(tt)> 1.5*buffersize:
            nchunks = int(len(tt)/buffersize+1)
            tt_chunks = np.array_split(tt, nchunks)
            return stacker([self.to_soundarray(tt=ttc, buffersize=buffersize, fps=fps,
                                        quantize=quantize, nbytes=nbytes)
                              for ttc in tt_chunks])
        """
        snd_array = self.get_frame(tt)

        if quantize:
            snd_array = np.maximum(-0.99, np.minimum(0.99, snd_array))
            inttype = {1: "int8", 2: "int16", 4: "int32"}[nbytes]
            snd_array = (2 ** (8 * nbytes - 1) * snd_array).astype(inttype)

        return snd_array

    def max_volume(self, stereo=False, chunksize=50000, logger=None):
        """Returns the maximum volume level of the clip."""
        # max volume separated by channels if ``stereo`` and not mono
        stereo = stereo and self.nchannels > 1

        # zero for each channel
        maxi = np.zeros(self.nchannels)
        for chunk in self.iter_chunks(chunksize=chunksize, logger=logger):
            maxi = np.maximum(maxi, abs(chunk).max(axis=0))

        # if mono returns float, otherwise array of volumes by channel
        return maxi if stereo else maxi[0]

    @requires_duration
    @convert_path_to_string("filename")
    def write_audiofile(
        self,
        filename,
        fps=None,
        nbytes=2,
        buffersize=2000,
        codec=None,
        bitrate=None,
        ffmpeg_params=None,
        write_logfile=False,
        logger="bar",
    ):
        """Writes an audio file from the AudioClip.


        Parameters
        ----------

        filename
          Name of the output file, as a string or a path-like object.

        fps
          Frames per second. If not set, it will try default to self.fps if
          already set, otherwise it will default to 44100.

        nbytes
          Sample width (set to 2 for 16-bit sound, 4 for 32-bit sound)

        codec
          Which audio codec should be used. If None provided, the codec is
          determined based on the extension of the filename. Choose
          'pcm_s16le' for 16-bit wav and 'pcm_s32le' for 32-bit wav.

        bitrate
          Audio bitrate, given as a string like '50k', '500k', '3000k'.
          Will determine the size and quality of the output file.
          Note that it mainly an indicative goal, the bitrate won't
          necessarily be the this in the output file.

        ffmpeg_params
          Any additional parameters you would like to pass, as a list
          of terms, like ['-option1', 'value1', '-option2', 'value2']

        write_logfile
          If true, produces a detailed logfile named filename + '.log'
          when writing the file

        logger
          Either ``"bar"`` for progress bar or ``None`` or any Proglog logger.

        """
        if not fps:
            if not self.fps:
                fps = 44100
            else:
                fps = self.fps

        if codec is None:
            name, ext = os.path.splitext(os.path.basename(filename))
            try:
                codec = extensions_dict[ext[1:]]["codec"][0]
            except KeyError:
                raise ValueError(
                    "MoviePy couldn't find the codec associated "
                    "with the filename. Provide the 'codec' "
                    "parameter in write_audiofile."
                )

        return ffmpeg_audiowrite(
            self,
            filename,
            fps,
            nbytes,
            buffersize,
            codec=codec,
            bitrate=bitrate,
            write_logfile=write_logfile,
            ffmpeg_params=ffmpeg_params,
            logger=logger,
        )


class AudioArrayClip(AudioClip):
    """

    An audio clip made from a sound array.

    Parameters
    ----------

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

        def make_frame(t):
            """Complicated, but must be able to handle the case where t
            is a list of the form sin(t).
            """
            if isinstance(t, np.ndarray):
                array_inds = np.round(self.fps * t).astype(int)
                in_array = (array_inds >= 0) & (array_inds < len(self.array))
                result = np.zeros((len(t), 2))
                result[in_array] = self.array[array_inds[in_array]]
                return result
            else:
                i = int(self.fps * t)
                if i < 0 or i >= len(self.array):
                    return 0 * self.array[0]
                else:
                    return self.array[i]

        self.make_frame = make_frame
        self.nchannels = len(list(self.get_frame(0)))


class CompositeAudioClip(AudioClip):
    """Clip made by composing several AudioClips.

    An audio clip made by putting together several audio clips.

    Parameters
    ----------

    clips
      List of audio clips, which may start playing at different times or
      together, depends on their ``start`` attributes. If all have their
      ``duration`` attribute set, the duration of the composite clip is
      computed automatically.
    """

    def __init__(self, clips):
        self.clips = clips
        self.nchannels = max(clip.nchannels for clip in self.clips)

        # self.duration is set at AudioClip
        duration = None
        for end in self.ends:
            if end is None:
                break
            duration = max(end, duration or 0)

        # self.fps is set at AudioClip
        fps = None
        for clip in self.clips:
            if hasattr(clip, "fps") and isinstance(clip.fps, numbers.Number):
                fps = max(clip.fps, fps or 0)

        super().__init__(duration=duration, fps=fps)

    @property
    def starts(self):
        """Returns starting times for all clips in the composition."""
        return (clip.start for clip in self.clips)

    @property
    def ends(self):
        """Returns ending times for all clips in the composition."""
        return (clip.end for clip in self.clips)

    def make_frame(self, t):
        """Renders a frame for the composition for the time ``t``."""
        played_parts = [clip.is_playing(t) for clip in self.clips]

        sounds = [
            clip.get_frame(t - clip.start) * np.array([part]).T
            for clip, part in zip(self.clips, played_parts)
            if (part is not False)
        ]

        if isinstance(t, np.ndarray):
            zero = np.zeros((len(t), self.nchannels))
        else:
            zero = np.zeros(self.nchannels)

        return zero + sum(sounds)


def concatenate_audioclips(clips):
    """Concatenates one AudioClip after another, in the order that are passed
    to ``clips`` parameter.

    Parameters
    ----------

    clips
      List of audio clips, which will be played one after other.
    """
    # start, end/start2, end2/start3... end
    starts_end = np.cumsum([0, *[clip.duration for clip in clips]])
    newclips = [clip.with_start(t) for clip, t in zip(clips, starts_end[:-1])]

    return CompositeAudioClip(newclips).with_duration(starts_end[-1])
