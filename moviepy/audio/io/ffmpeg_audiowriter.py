import subprocess as sp
import os
import proglog

from moviepy.compat import DEVNULL

from moviepy.config import get_setting
from moviepy.decorators import requires_duration


class FFMPEG_AudioWriter:
    """
    A class to write an AudioClip into an audio file.

    Parameters
    ------------

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

    def __init__(self, filename, fps_input, nbytes=2,
                 nchannels=2, codec='libfdk_aac', bitrate=None,
                 input_video=None, logfile=None, ffmpeg_params=None):

        self.filename = filename
        self.codec = codec

        if logfile is None:
            logfile = sp.PIPE

        cmd = ([get_setting("FFMPEG_BINARY"), '-y',
                "-loglevel", "error" if logfile == sp.PIPE else "info",
                "-f", 's%dle' % (8*nbytes),
                "-acodec",'pcm_s%dle' % (8*nbytes),
                '-ar', "%d" % fps_input,
                '-ac', "%d" % nchannels,
                '-i', '-']
               + (['-vn'] if input_video is None else ["-i", input_video, '-vcodec', 'copy'])
               + ['-acodec', codec]
               + ['-ar', "%d" % fps_input]
               + ['-strict', '-2']  # needed to support codec 'aac'
               + (['-ab', bitrate] if (bitrate is not None) else [])
               + (ffmpeg_params if ffmpeg_params else [])
               + [filename])

        popen_params = {"stdout": DEVNULL,
                        "stderr": logfile,
                        "stdin": sp.PIPE}

        if os.name == "nt":
            popen_params["creationflags"] = 0x08000000

        self.proc = sp.Popen(cmd, **popen_params)

    def write_frames(self, frames_array):
        try:
            try:
                self.proc.stdin.write(frames_array.tobytes())
            except NameError:
                self.proc.stdin.write(frames_array.tostring())
        except IOError as err:
            ffmpeg_error = self.proc.stderr.read()
            error = (str(err) + ("\n\nMoviePy error: FFMPEG encountered "
                                 "the following error while writing file %s:" % self.filename
                                 + "\n\n" + str(ffmpeg_error)))

            if b"Unknown encoder" in ffmpeg_error:

                error = (error +
                         ("\n\nThe audio export failed because FFMPEG didn't "
                          "find the specified codec for audio encoding (%s). "
                          "Please install this codec or change the codec when "
                          "calling to_videofile or to_audiofile. For instance "
                          "for mp3:\n"
                          "   >>> to_videofile('myvid.mp4', audio_codec='libmp3lame')"
                          ) % (self.codec))

            elif b"incorrect codec parameters ?" in ffmpeg_error:

                error = (error +
                         ("\n\nThe audio export failed, possibly because the "
                          "codec specified for the video (%s) is not compatible"
                          " with the given extension (%s). Please specify a "
                          "valid 'codec' argument in to_videofile. This would "
                          "be 'libmp3lame' for mp3, 'libvorbis' for ogg...")
                         % (self.codec, self.ext))

            elif b"encoder setup failed" in ffmpeg_error:

                error = (error +
                         ("\n\nThe audio export failed, possily because the "
                          "bitrate you specified was two high or too low for "
                          "the video codec."))

            else:
                error = (error +
                         ("\n\nIn case it helps, make sure you are using a "
                          "recent version of FFMPEG (the versions in the "
                          "Ubuntu/Debian repos are deprecated)."))

            raise IOError(error)

    def close(self):
        if self.proc:
            self.proc.stdin.close()
            self.proc.stdin = None
            if self.proc.stderr is not None:
                self.proc.stderr.close()
                self.proc.stdee = None
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
def ffmpeg_audiowrite(clip, filename, fps, nbytes, buffersize,
                      codec='libvorbis', bitrate=None,
                      write_logfile=False, verbose=True,
                      ffmpeg_params=None, logger='bar'):
    """
    A function that wraps the FFMPEG_AudioWriter to write an AudioClip
    to a file.

    NOTE: verbose is deprecated.
    """

    if write_logfile:
        logfile = open(filename + ".log", 'w+')
    else:
        logfile = None
    logger = proglog.default_bar_logger(logger)
    logger(message="MoviePy - Writing audio in %s")
    writer = FFMPEG_AudioWriter(filename, fps, nbytes, clip.nchannels,
                                codec=codec, bitrate=bitrate,
                                logfile=logfile,
                                ffmpeg_params=ffmpeg_params)

    for chunk in clip.iter_chunks(chunksize=buffersize,
                                  quantize=True,
                                  nbytes=nbytes, fps=fps,
                                  logger=logger):
        writer.write_frames(chunk)

    writer.close()

    if write_logfile:
        logfile.close()
    logger(message="MoviePy - Done.")