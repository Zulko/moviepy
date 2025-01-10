"""Implements AudioFileClip, a class for audio clips creation using audio files."""

from moviepy.audio.AudioClip import AudioClip
from moviepy.audio.io.readers import FFMPEG_AudioReader
from moviepy.decorators import convert_path_to_string


class AudioFileClip(AudioClip):
    """
    An audio clip read from a sound file, or an array.
    The whole file is not loaded in memory. Instead, only a portion is
    read and stored in memory. this portion includes frames before
    and after the last frames read, so that it is fast to read the sound
    backward and forward.

    Parameters
    ----------

    filename
      Either a soundfile name (of any extension supported by ffmpeg)
      as a string or a path-like object,
      or an array representing a sound. If the soundfile is not a .wav,
      it will be converted to .wav first, using the ``fps`` and
      ``bitrate`` arguments.

    buffersize:
      Size to load in memory (in number of frames)


    Attributes
    ----------

    nbytes
      Number of bits per frame of the original audio file.

    fps
      Number of frames per second in the audio file

    buffersize
      See Parameters.

    Lifetime
    --------

    Note that this creates subprocesses and locks files. If you construct one
    of these instances, you must call close() afterwards, or the subresources
    will not be cleaned up until the process ends.

    Examples
    --------

    .. code:: python

        snd = AudioFileClip("song.wav")
        snd.close()
    """

    @convert_path_to_string("filename")
    def __init__(
        self, filename, decode_file=False, buffersize=200000, nbytes=2, fps=44100
    ):
        AudioClip.__init__(self)

        self.filename = filename
        self.reader = FFMPEG_AudioReader(
            filename,
            decode_file=decode_file,
            fps=fps,
            nbytes=nbytes,
            buffersize=buffersize,
        )
        self.fps = fps
        self.duration = self.reader.duration
        self.end = self.reader.duration
        self.buffersize = self.reader.buffersize
        self.filename = filename

        self.frame_function = lambda t: self.reader.get_frame(t)
        self.nchannels = self.reader.nchannels

    def close(self):
        """Close the internal reader."""
        if self.reader:
            self.reader.close()
            self.reader = None
