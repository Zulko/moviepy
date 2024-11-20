"""MoviePy audio reading with ffmpeg."""

import subprocess as sp
import warnings

import numpy as np

from moviepy.config import FFMPEG_BINARY
from moviepy.tools import cross_platform_popen_params
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos


class FFMPEG_AudioReader:
    """A class to read the audio in either video files or audio files
    using ffmpeg. ffmpeg will read any audio and transform them into
    raw data.

    Parameters
    ----------

    filename
      Name of any video or audio file, like ``video.mp4`` or
      ``sound.wav`` etc.

    buffersize
      The size of the buffer to use. Should be bigger than the buffer
      used by ``write_audiofile``

    print_infos
      Print the ffmpeg infos on the file being read (for debugging)

    fps
      Desired frames per second in the decoded signal that will be
      received from ffmpeg

    nbytes
      Desired number of bytes (1,2,4) in the signal that will be
      received from ffmpeg
    """

    def __init__(
        self,
        filename,
        buffersize,
        decode_file=False,
        print_infos=False,
        fps=44100,
        nbytes=2,
        nchannels=2,
    ):
        # TODO bring FFMPEG_AudioReader more in line with FFMPEG_VideoReader
        # E.g. here self.pos is still 1-indexed.
        # (or have them inherit from a shared parent class)
        self.filename = filename
        self.nbytes = nbytes
        self.fps = fps
        self.format = "s%dle" % (8 * nbytes)
        self.codec = "pcm_s%dle" % (8 * nbytes)
        self.nchannels = nchannels
        infos = ffmpeg_parse_infos(filename, decode_file=decode_file)
        self.duration = infos["duration"]
        self.bitrate = infos["audio_bitrate"]
        self.infos = infos
        self.proc = None

        self.n_frames = int(self.fps * self.duration)
        self.buffersize = min(self.n_frames + 1, buffersize)
        self.buffer = None
        self.buffer_startframe = 1
        self.initialize()
        self.buffer_around(1)

    def initialize(self, start_time=0):
        """Opens the file, creates the pipe."""
        self.close()  # if any

        if start_time != 0:
            offset = min(1, start_time)
            i_arg = [
                "-ss",
                "%.05f" % (start_time - offset),
                "-i",
                self.filename,
                "-vn",
                "-ss",
                "%.05f" % offset,
            ]
        else:
            i_arg = ["-i", self.filename, "-vn"]

        cmd = (
            [FFMPEG_BINARY]
            + i_arg
            + [
                "-loglevel",
                "error",
                "-f",
                self.format,
                "-acodec",
                self.codec,
                "-ar",
                "%d" % self.fps,
                "-ac",
                "%d" % self.nchannels,
                "-",
            ]
        )

        popen_params = cross_platform_popen_params(
            {
                "bufsize": self.buffersize,
                "stdout": sp.PIPE,
                "stderr": sp.PIPE,
                "stdin": sp.DEVNULL,
            }
        )

        self.proc = sp.Popen(cmd, **popen_params)

        self.pos = np.round(self.fps * start_time)

    def skip_chunk(self, chunksize):
        """Skip a chunk of audio data by reading and discarding the specified number of
        frames from the audio stream. The audio stream is read from the `proc` stdout.
        After skipping the chunk, the `pos` attribute is updated accordingly.

        Parameters
        ----------
        chunksize (int):
          The number of audio frames to skip.
        """
        _ = self.proc.stdout.read(self.nchannels * chunksize * self.nbytes)
        self.proc.stdout.flush()
        self.pos = self.pos + chunksize

    def read_chunk(self, chunksize):
        """Read a chunk of audio data from the audio stream.

        This method reads a chunk of audio data from the audio stream. The
        specified number of frames, given by `chunksize`, is read from the
        `proc` stdout. The audio data is returned as a NumPy array, where
        each row corresponds to a frame and each column corresponds to a
        channel. If there is not enough audio left to read, the remaining
        portion is padded with zeros, ensuring that the returned array has
        the desired length. The `pos` attribute is updated accordingly.

        Parameters
        ----------
        chunksize (float):
          The desired number of audio frames to read.

        """
        # chunksize is not being autoconverted from float to int
        chunksize = int(round(chunksize))
        s = self.proc.stdout.read(self.nchannels * chunksize * self.nbytes)
        data_type = {1: "int8", 2: "int16", 4: "int32"}[self.nbytes]
        if hasattr(np, "frombuffer"):
            result = np.frombuffer(s, dtype=data_type)
        else:
            result = np.fromstring(s, dtype=data_type)
        result = (1.0 * result / 2 ** (8 * self.nbytes - 1)).reshape(
            (int(len(result) / self.nchannels), self.nchannels)
        )

        # Pad the read chunk with zeros when there isn't enough audio
        # left to read, so the buffer is always at full length.
        pad = np.zeros((chunksize - len(result), self.nchannels), dtype=result.dtype)
        result = np.concatenate([result, pad])
        # self.proc.stdout.flush()
        self.pos = self.pos + chunksize
        return result

    def seek(self, pos):
        """Read a frame at time t. Note for coders: getting an arbitrary
        frame in the video with ffmpeg can be painfully slow if some
        decoding has to be done. This function tries to avoid fectching
        arbitrary frames whenever possible, by moving between adjacent
        frames.
        """
        if (pos < self.pos) or (pos > (self.pos + 1000000)):
            t = 1.0 * pos / self.fps
            self.initialize(t)
        elif pos > self.pos:
            # print pos
            self.skip_chunk(pos - self.pos)
        # last case standing: pos = current pos
        self.pos = pos

    def get_frame(self, tt):
        """Retrieve the audio frame(s) corresponding to the given timestamp(s).

        Parameters
        ----------
        tt (float or numpy.ndarray):
          The timestamp(s) at which to retrieve the audio frame(s).
          If `tt` is a single float value, the frame corresponding to that
          timestamp is returned. If `tt` is a NumPy array of timestamps, an
          array of frames corresponding to each timestamp is returned.
        """
        if isinstance(tt, np.ndarray):
            # lazy implementation, but should not cause problems in
            # 99.99 %  of the cases

            # elements of t that are actually in the range of the
            # audio file.
            in_time = (tt >= 0) & (tt < self.duration)

            # Check that the requested time is in the valid range
            if not in_time.any():
                raise IOError(
                    "Error in file %s, " % (self.filename)
                    + "Accessing time t=%.02f-%.02f seconds, " % (tt[0], tt[-1])
                    + "with clip duration=%f seconds, " % self.duration
                )

            # The np.round in the next line is super-important.
            # Removing it results in artifacts in the noise.
            frames = np.round((self.fps * tt)).astype(int)[in_time]
            fr_min, fr_max = frames.min(), frames.max()

            if not (0 <= (fr_min - self.buffer_startframe) < len(self.buffer)):
                self.buffer_around(fr_min)
            elif not (0 <= (fr_max - self.buffer_startframe) < len(self.buffer)):
                self.buffer_around(fr_max)

            try:
                result = np.zeros((len(tt), self.nchannels))
                indices = frames - self.buffer_startframe
                result[in_time] = self.buffer[indices]
                return result

            except IndexError as error:
                warnings.warn(
                    "Error in file %s, " % (self.filename)
                    + "At time t=%.02f-%.02f seconds, " % (tt[0], tt[-1])
                    + "indices wanted: %d-%d, " % (indices.min(), indices.max())
                    + "but len(buffer)=%d\n" % (len(self.buffer))
                    + str(error),
                    UserWarning,
                )

                # repeat the last frame instead
                indices[indices >= len(self.buffer)] = len(self.buffer) - 1
                result[in_time] = self.buffer[indices]
                return result

        else:
            ind = int(self.fps * tt)
            if ind < 0 or ind > self.n_frames:  # out of time: return 0
                return np.zeros(self.nchannels)

            if not (0 <= (ind - self.buffer_startframe) < len(self.buffer)):
                # out of the buffer: recenter the buffer
                self.buffer_around(ind)

            # read the frame in the buffer
            return self.buffer[ind - self.buffer_startframe]

    def buffer_around(self, frame_number):
        """Fill the buffer with frames, centered on frame_number if possible."""
        # start-frame for the buffer
        new_bufferstart = max(0, frame_number - self.buffersize // 2)

        if self.buffer is not None:
            current_f_end = self.buffer_startframe + self.buffersize
            if new_bufferstart < current_f_end < new_bufferstart + self.buffersize:
                # We already have part of what must be read
                conserved = current_f_end - new_bufferstart
                chunksize = self.buffersize - conserved
                array = self.read_chunk(chunksize)
                self.buffer = np.vstack([self.buffer[-conserved:], array])
            else:
                self.seek(new_bufferstart)
                self.buffer = self.read_chunk(self.buffersize)
        else:
            self.seek(new_bufferstart)
            self.buffer = self.read_chunk(self.buffersize)

        self.buffer_startframe = new_bufferstart

    def close(self):
        """Closes the reader, terminating the subprocess if is still alive."""
        if self.proc:
            if self.proc.poll() is None:
                self.proc.terminate()
                self.proc.stdout.close()
                self.proc.stderr.close()
                self.proc.wait()
            self.proc = None

    def __del__(self):
        # If the garbage collector comes, make sure the subprocess is terminated.
        self.close()
