"""
On the long term this will implement several methods to make videos
out of VideoClips
"""

import subprocess as sp

from moviepy.config import FFPLAY_BINARY
from moviepy.tools import cross_platform_popen_params


class FFPLAY_VideoPreviewer:
    """A class for FFPLAY-based video preview.

    Parameters
    ----------

    size : tuple or list
      Size of the output video in pixels (width, height).

    fps : int
      Frames per second in the output video file.

    pixel_format : str
      Pixel format for the output video file, ``rgb24`` for normal video, ``rgba``
      if video with mask.
    """

    def __init__(
        self,
        size,
        fps,
        pixel_format,
    ):
        # order is important
        cmd = [
            FFPLAY_BINARY,
            "-autoexit",  # If you don't precise, ffplay won't stop at end
            "-f",
            "rawvideo",
            "-pixel_format",
            pixel_format,
            "-video_size",
            "%dx%d" % (size[0], size[1]),
            "-framerate",
            "%.02f" % fps,
            "-",
        ]

        popen_params = cross_platform_popen_params(
            {"stdout": sp.DEVNULL, "stderr": sp.STDOUT, "stdin": sp.PIPE}
        )

        self.proc = sp.Popen(cmd, **popen_params)

    def show_frame(self, img_array):
        """Writes one frame in the file."""
        try:
            self.proc.stdin.write(img_array.tobytes())
        except IOError as err:
            _, ffplay_error = self.proc.communicate()
            if ffplay_error is not None:
                ffplay_error = ffplay_error.decode()

            error = (
                f"{err}\n\nMoviePy error: FFPLAY encountered the following error while "
                f"previewing clip :\n\n {ffplay_error}"
            )

            raise IOError(error)

    def close(self):
        """Closes the writer, terminating the subprocess if is still alive."""
        if self.proc:
            self.proc.stdin.close()
            if self.proc.stderr is not None:
                self.proc.stderr.close()
            self.proc.wait()

            self.proc = None

    # Support the Context Manager protocol, to ensure that resources are cleaned up.

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def ffplay_preview_video(
    clip, fps, pixel_format="rgb24", audio_flag=None, video_flag=None
):
    """Preview the clip using ffplay. See VideoClip.preview for details
    on the parameters.

    Parameters
    ----------

    clip : VideoClip
      The clip to preview

    fps : int
      Number of frames per seconds in the displayed video.

    pixel_format : str, optional
      Warning: This is not used anywhere in the code and should probably
      be removed.
      It is believed pixel format rgb24 does not work properly for now because
      it requires applying a mask on CompositeVideoClip and that is believed to
      not be working.

      Pixel format for the output video file, ``rgb24`` for normal video, ``rgba``
      if video with mask

    audio_flag : Thread.Event, optional
      A thread event that video will wait for. If not provided we ignore audio

    video_flag : Thread.Event, optional
      A thread event that video will set after first frame has been shown. If not
      provided, we simply ignore
    """
    with FFPLAY_VideoPreviewer(clip.size, fps, pixel_format) as previewer:
        first_frame = True
        for t, frame in clip.iter_frames(with_times=True, fps=fps, dtype="uint8"):
            previewer.show_frame(frame)

            # After first frame is shown, if we have audio/video flag, set video ready
            # and wait for audio
            if first_frame:
                first_frame = False

                if video_flag:
                    video_flag.set()  # say to the audio: video is ready

                if audio_flag:
                    audio_flag.wait()  # wait for the audio to be ready
