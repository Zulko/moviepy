from __future__ import division

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

    filename
      Either a soundfile name (of any extension supported by ffmpeg)
      or an array representing a sound. If the soundfile is not a .wav,
      it will be converted to .wav first, using the ``fps`` and
      ``bitrate`` arguments.

    buffersize:
      Size to load in memory (in number of frames)


    Attributes
    ------------

    nbytes
      Number of bits per frame of the original audio file.

    fps
      Number of frames per second in the audio file

    buffersize
      See Parameters.

    Lifetime
    --------

    Note that this creates subprocesses and locks files. If you construct one of these instances, you must call
    close() afterwards, or the subresources will not be cleaned up until the process ends.

    If copies are made, and close() is called on one, it may cause methods on the other copies to fail.

    However, coreaders must be closed separately.

    Examples
    ----------

    >>> snd = AudioFileClip("song.wav")
    >>> snd.close()
    >>> snd = AudioFileClip("song.mp3", fps = 44100)
    >>> second_reader = snd.coreader()
    >>> second_reader.close()
    >>> snd.close()
    >>> with AudioFileClip(mySoundArray, fps=44100) as snd:  # from a numeric array
    >>>     pass  # Close is implicitly performed by context manager.

    """

    def __init__(self, filename, buffersize=200000, nbytes=2, fps=44100):

        AudioClip.__init__(self)

        self.filename = filename
        self.reader = FFMPEG_AudioReader(filename, fps=fps, nbytes=nbytes,
                                         buffersize=buffersize)
        self.fps = fps
        self.duration = self.reader.duration
        self.end = self.reader.duration
        self.buffersize = self.reader.buffersize

        self.make_frame = lambda t: self.reader.get_frame(t)
        self.nchannels = self.reader.nchannels

    def coreader(self):
        """ Returns a copy of the AudioFileClip, i.e. a new entrance point
            to the audio file. Use copy when you have different clips
            watching the audio file at different times. """
        return AudioFileClip(self.filename, self.buffersize)

    def close(self):
        """ Close the internal reader. """
        if self.reader:
            self.reader.close_proc()
            self.reader = None
