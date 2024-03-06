"""MoviePy audio writing with ffmpeg."""

import subprocess as sp

import proglog

from moviepy.config import FFMPEG_BINARY
from moviepy.decorators import requires_duration
from moviepy.tools import cross_platform_popen_params


class FFMPEG_AudioWriter:
    """
    A class to write an AudioClip into an audio file.

    Parameters
    ----------

    filename
      Name of any video or audio file, like ``video.mp4`` or ``sound.wav`` etc.

    size
      Size (width,height) in pixels of the output video.

    fps_input
      Frames per second of the input audio (given by the AUdioClip being
      written down).

    codec
      Name of the ffmpeg codec to use for the output.

    bitrate:
      A string indicating the bitrate of the final video. Only
      relevant for codecs which accept a bitrate.

    """

    def __init__(
        self,
        filename,
        fps_input,
        nbytes=2,
        nchannels=2,
        codec="libfdk_aac",
        bitrate=None,
        input_video=None,
        logfile=None,
        ffmpeg_params=None,
    ):
        if logfile is None:
            logfile = sp.PIPE
        self.logfile = logfile
        self.filename = filename
        self.codec = codec
        self.ext = self.filename.split(".")[-1]

        # order is important
        cmd = [
            FFMPEG_BINARY,
            "-y",
            "-loglevel",
            "error" if logfile == sp.PIPE else "info",
            "-f",
            "s%dle" % (8 * nbytes),
            "-acodec",
            "pcm_s%dle" % (8 * nbytes),
            "-ar",
            "%d" % fps_input,
            "-ac",
            "%d" % nchannels,
            "-i",
            "-",
        ]
        if input_video is None:
            cmd.extend(["-vn"])
        else:
            cmd.extend(["-i", input_video, "-vcodec", "copy"])

        cmd.extend(["-acodec", codec] + ["-ar", "%d" % fps_input])
        cmd.extend(["-strict", "-2"])  # needed to support codec 'aac'
        if bitrate is not None:
            cmd.extend(["-ab", bitrate])
        if ffmpeg_params is not None:
            cmd.extend(ffmpeg_params)
        cmd.extend([filename])

        popen_params = cross_platform_popen_params(
            {"stdout": sp.DEVNULL, "stderr": logfile, "stdin": sp.PIPE}
        )

        self.proc = sp.Popen(cmd, **popen_params)

    def write_frames(self, frames_array):
        """Send the audio frame (a chunck of ``AudioClip``) to ffmpeg for writting"""
        try:
            self.proc.stdin.write(frames_array.tobytes())
        except IOError as err:
            _, ffmpeg_error = self.proc.communicate()
            if ffmpeg_error is not None:
                ffmpeg_error = ffmpeg_error.decode()
            else:
                # The error was redirected to a logfile with `write_logfile=True`,
                # so read the error from that file instead
                self.logfile.seek(0)
                ffmpeg_error = self.logfile.read()

            error = (
                f"{err}\n\nMoviePy error: FFMPEG encountered the following error while "
                f"writing file {self.filename}:\n\n {ffmpeg_error}"
            )

            if "Unknown encoder" in ffmpeg_error:
                error += (
                    "\n\nThe audio export failed because FFMPEG didn't find the "
                    f"specified codec for audio encoding {self.codec}. "
                    "Please install this codec or change the codec when calling "
                    "write_videofile or write_audiofile.\nFor instance for mp3:\n"
                    "   >>> write_videofile('myvid.mp4', audio_codec='libmp3lame')"
                )

            elif "incorrect codec parameters ?" in ffmpeg_error:
                error += (
                    "\n\nThe audio export failed, possibly because the "
                    f"codec specified for the video {self.codec} is not compatible"
                    f" with the given extension {self.ext}. Please specify a "
                    "valid 'codec' argument in write_audiofile or 'audio_codoc'"
                    "argument in write_videofile. This would be "
                    "'libmp3lame' for mp3, 'libvorbis' for ogg..."
                )

            elif "bitrate not specified" in ffmpeg_error:
                error += (
                    "\n\nThe audio export failed, possibly because the "
                    "bitrate you specified was too high or too low for "
                    "the audio codec."
                )

            elif "Invalid encoder type" in ffmpeg_error:
                error += (
                    "\n\nThe audio export failed because the codec "
                    "or file extension you provided is not suitable for audio"
                )

            raise IOError(error)

    def close(self):
        """Closes the writer, terminating the subprocess if is still alive."""
        if hasattr(self, "proc") and self.proc:
            self.proc.stdin.close()
            self.proc.stdin = None
            if self.proc.stderr is not None:
                self.proc.stderr.close()
                self.proc.stderr = None
            # If this causes deadlocks, consider terminating instead.
            self.proc.wait()
            self.proc = None

    def __del__(self):
        # If the garbage collector comes, make sure the subprocess is terminated.
        self.close()

    # Support the Context Manager protocol, to ensure that resources are cleaned up.

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


@requires_duration
def ffmpeg_audiowrite(
    clip,
    filename,
    fps,
    nbytes,
    buffersize,
    codec="libvorbis",
    bitrate=None,
    write_logfile=False,
    ffmpeg_params=None,
    logger="bar",
):
    """
    A function that wraps the FFMPEG_AudioWriter to write an AudioClip
    to a file.
    """
    if write_logfile:
        logfile = open(filename + ".log", "w+")
    else:
        logfile = None
    logger = proglog.default_bar_logger(logger)
    logger(message="MoviePy - Writing audio in %s" % filename)
    writer = FFMPEG_AudioWriter(
        filename,
        fps,
        nbytes,
        clip.nchannels,
        codec=codec,
        bitrate=bitrate,
        logfile=logfile,
        ffmpeg_params=ffmpeg_params,
    )

    for chunk in clip.iter_chunks(
        chunksize=buffersize, quantize=True, nbytes=nbytes, fps=fps, logger=logger
    ):
        writer.write_frames(chunk)

    writer.close()

    if write_logfile:
        logfile.close()
    logger(message="MoviePy - Done.")
