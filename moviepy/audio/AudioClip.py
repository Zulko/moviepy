"""Implements AudioClip (base class for audio clips) and its main subclasses:

- Audio clips: AudioClip, AudioFileClip, AudioArrayClip
- Composition: CompositeAudioClip
"""

import numbers
import os

import numpy as np
import proglog

from moviepy.audio.io.ffmpeg_audiowriter import ffmpeg_audiowrite
from moviepy.audio.io.ffplay_audiopreviewer import ffplay_audiopreview
from moviepy.Clip import Clip
from moviepy.decorators import convert_path_to_string, requires_duration
from moviepy.tools import extensions_dict


class AudioClip(Clip):
    """
    音频剪辑的基类。

    有关可用的类，请参见 ``AudioFileClip`` 和 ``CompositeAudioClip``。

    AudioClip 是一个 Clip，其 ``frame_function`` 属性的形式为
    ``t -> [ f_t ]``（对于单声道声音）和 ``t-> [ f1_t, f2_t ]``（对于立体声声音）（数组是 Numpy 数组）。
    `f_t` 是介于 -1 和 1 之间的浮点数。这些边界可以被超越而没有问题
    （程序将在转换时将声音放回边界内，而不会产生太大影响）。

    Parameters
    ----------

    frame_function
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
    .. code:: python
        # 以单声道播放音符 A（频率为 440 Hz 的正弦波）
        import numpy as np
        frame_function = lambda t: np.sin(440 * 2 * np.pi * t)
        clip = AudioClip(frame_function, duration=5, fps=44100)
        clip.preview()

        # 以立体声播放音符 A（频率为 440 和 880 Hz 的两个正弦波）
        frame_function = lambda t: np.array([
            np.sin(440 * 2 * np.pi * t),
            np.sin(880 * 2 * np.pi * t)
        ]).T.copy(order="C")
        clip = AudioClip(frame_function, duration=3, fps=44100)
        clip.preview()
    """

    def __init__(
            self,
            frame_function=None,  # 一个函数 `t-> 时间 t 的帧`。帧对于声音来说意义不大，它只是一个浮点数。 “产生”声音的是该浮点数在时间上的变化。
            duration=None,  # 剪辑的持续时间（以秒为单位）。有些剪辑是无限的，在这种情况下，它们的持续时间将为 ``None``。
            fps=None  # 声道数（单声道或立体声为一或二）。
    ):
        super().__init__()

        if fps is not None:
            self.fps = fps

        if frame_function is not None:
            self.frame_function = frame_function
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

        buffersize
          The sound is not generated all at once, but rather made by bunches
          of frames (chunks). ``buffersize`` is the size of such a chunk.
          Try varying it if you meet audio problems (but you shouldn't
          have to). Default to 2000

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
            if hasattr(self, "fps"):
                fps = self.fps
            else:
                fps = 44100

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

    @requires_duration
    def audiopreview(
            self, fps=None, buffersize=2000, nbytes=2, audio_flag=None, video_flag=None
    ):
        """
        Preview an AudioClip using ffplay

        Parameters
        ----------

        fps
            Frame rate of the sound. 44100 gives top quality, but may cause
            problems if your computer is not fast enough and your clip is
            complicated. If the sound jumps during the preview, lower it
            (11025 is still fine, 5000 is tolerable).

        buffersize
            The sound is not generated all at once, but rather made by bunches
            of frames (chunks). ``buffersize`` is the size of such a chunk.
            Try varying it if you meet audio problems (but you shouldn't
            have to).

        nbytes:
            Number of bytes to encode the sound: 1 for 8bit sound, 2 for
            16bit, 4 for 32bit sound. 2 bytes is fine.

        audio_flag, video_flag:
            Instances of class threading events that are used to synchronize
            video and audio during ``VideoClip.preview()``.
        """
        ffplay_audiopreview(
            clip=self,
            fps=fps,
            buffersize=buffersize,
            nbytes=nbytes,
            audio_flag=audio_flag,
            video_flag=video_flag,
        )

    def __add__(self, other):
        if isinstance(other, AudioClip):
            return concatenate_audioclips([self, other])
        return super(AudioClip, self).__add__(other)


class AudioArrayClip(AudioClip):
    """
    一个由声音数组组成的音频剪辑。
    """

    def __init__(
            self,
            array,  # 一个表示声音的 Numpy 数组，对于单声道为 Nx1 大小，对于立体声为 Nx2 大小。
            fps  # 每秒帧数：声音应该播放的速度。
    ):
        Clip.__init__(self)
        self.array = array
        self.fps = fps
        self.duration = 1.0 * len(array) / fps

        def frame_function(t):
            """ 很复杂，但必须能够处理 t 是 sin(t) 形式列表的情况。"""
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

        self.frame_function = frame_function
        self.nchannels = len(list(self.get_frame(0)))


class CompositeAudioClip(AudioClip):
    """
    通过组合多个 AudioClip 创建的剪辑。 通过将多个音频剪辑放在一起来创建的音频剪辑。

    参数
    ----------
    clips
      音频剪辑列表，可以根据其 ``start`` 属性在不同的时间或一起开始播放。
      如果所有剪辑都设置了 ``duration`` 属性，则会自动计算复合剪辑的持续时间。
    """

    def __init__(self, clips):
        self.clips = clips
        self.nchannels = max(clip.nchannels for clip in self.clips)

        # self.duration 在 AudioClip 上设置
        duration = None
        for end in self.ends:
            if end is None:
                break
            duration = max(end, duration or 0)

        # self.fps 在 AudioClip 处设置
        fps = None
        for clip in self.clips:
            if hasattr(clip, "fps") and isinstance(clip.fps, numbers.Number):
                fps = max(clip.fps, fps or 0)

        super().__init__(duration=duration, fps=fps)

    @property
    def starts(self):
        """返回合成中所有剪辑的开始时间。"""
        return (clip.start for clip in self.clips)

    @property
    def ends(self):
        """返回合成中所有剪辑的结束时间。"""
        return (clip.end for clip in self.clips)

    def frame_function(self, t):
        """为时间“t”的合成渲染一帧。"""
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
