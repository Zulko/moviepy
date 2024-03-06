"""MoviePy audio writing with ffmpeg."""

import subprocess as sp

from moviepy.config import FFPLAY_BINARY
from moviepy.decorators import requires_duration
from moviepy.tools import cross_platform_popen_params


class FFPLAY_AudioPreviewer:
    """
    A class to preview an AudioClip.

    Parameters
    ----------

    fps_input
      Frames per second of the input audio (given by the AUdioClip being
      written down).

    nbytes:
      Number of bytes to encode the sound: 1 for 8bit sound, 2 for
      16bit, 4 for 32bit sound. Default is 2 bytes, it's fine.

    nchannels:
      Number of audio channels in the clip. Default to 2 channels.

    """

    def __init__(
        self,
        fps_input,
        nbytes=2,
        nchannels=2,
    ):
        # order is important
        cmd = [
            FFPLAY_BINARY,
            "-autoexit",  # If you dont precise, ffplay dont stop at end
            "-nodisp",  # If you dont precise a window is
            "-f",
            "s%dle" % (8 * nbytes),
            "-ar",
            "%d" % fps_input,
            "-ac",
            "%d" % nchannels,
            "-i",
            "-",
        ]

        popen_params = cross_platform_popen_params(
            {"stdout": sp.DEVNULL, "stderr": sp.STDOUT, "stdin": sp.PIPE}
        )

        self.proc = sp.Popen(cmd, **popen_params)

    def write_frames(self, frames_array):
        """Send a raw audio frame (a chunck of audio) to ffplay to be played"""
        try:
            self.proc.stdin.write(frames_array.tobytes())
        except IOError as err:
            _, ffplay_error = self.proc.communicate()
            if ffplay_error is not None:
                ffplay_error = ffplay_error.decode()
            else:
                # The error was redirected to a logfile with `write_logfile=True`,
                # so read the error from that file instead
                self.logfile.seek(0)
                ffplay_error = self.logfile.read()

            error = (
                f"{err}\n\nMoviePy error: FFPLAY encountered the following error while "
                f":\n\n {ffplay_error}"
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
def ffplay_audiopreview(
    clip, fps=None, buffersize=2000, nbytes=2, audio_flag=None, video_flag=None
):
    """
    A function that wraps the FFPLAY_AudioPreviewer to preview an AudioClip

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
    if not fps:
        if not clip.fps:
            fps = 44100
        else:
            fps = clip.fps

    with FFPLAY_AudioPreviewer(fps, nbytes, clip.nchannels) as previewer:
        first_frame = True
        for chunk in clip.iter_chunks(
            chunksize=buffersize, quantize=True, nbytes=nbytes, fps=fps
        ):
            # On first frame, wait for video
            if first_frame:
                first_frame = False

                if audio_flag is not None:
                    audio_flag.set()  # Say to video that audio is ready

                if video_flag is not None:
                    video_flag.wait()  # Wait for video to be ready

            previewer.write_frames(chunk)
