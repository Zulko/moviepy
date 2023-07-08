"""Video preview functions for MoviePy editor."""

import threading
import time
import numpy as np
from PIL import Image

from moviepy.decorators import (
    convert_masks_to_RGB,
    convert_parameter_to_seconds,
    requires_duration,
)
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

from moviepy.video.io.ffplay_previewer import ffplay_preview_video


@convert_masks_to_RGB
@convert_parameter_to_seconds(["t"])
def show(clip, t=0, with_mask=True):
    """
    Splashes the frame of clip corresponding to time ``t``.

    Parameters
    ----------

    t : float or tuple or str, optional
      Time in seconds of the frame to display.

    with_mask : bool, optional
      ``False`` if the clip has a mask but you want to see the clip without
      the mask.

    Examples
    --------

    >>> from moviepy.editor import *
    >>>
    >>> clip = VideoFileClip("media/chaplin.mp4")
    >>> clip.show(t=4, interactive=True)
    """
    if with_mask and (clip.mask is not None):
        clip = CompositeVideoClip([clip.with_position((0, 0))])

    img = clip.get_frame(t)
    pil_img = Image.fromarray(img)

    pil_img.show()


@requires_duration
@convert_masks_to_RGB
def preview(
    clip,
    fps=15,
    audio=True,
    audio_fps=22050,
    audio_buffersize=3000,
    audio_nbytes=2
):
    """
    Displays the clip in a window, at the given frames per second (of movie)
    rate. It will avoid that the clip be played faster than normal, but it
    cannot avoid the clip to be played slower than normal if the computations
    are complex. In this case, try reducing the ``fps``.

    Parameters
    ----------

    fps : int, optional
      Number of frames per seconds in the displayed video. Default to ``15``.

    audio : bool, optional
      ``True`` (default) if you want the clip's audio be played during
      the preview.

    audio_fps : int, optional
      The frames per second to use when generating the audio sound.

    audio_buffersize : int, optional
      The sized of the buffer used generating the audio sound.

    audio_nbytes : int, optional
      The number of bytes used generating the audio sound.

    Examples
    --------

    >>> from moviepy.editor import *
    >>>
    >>> clip = VideoFileClip("media/chaplin.mp4")
    >>> clip.preview(fps=10, audio=False)
    """

    audio = audio and (clip.audio is not None)
    audio_flag = None
    video_flag = None

    if audio:
        # the sound will be played in parallel. We are not
        # parralellizing it on different CPUs because it seems that
        # ffplay use several cpus.

        # two synchro-flags to tell whether audio and video are ready
        video_flag = threading.Event()
        audio_flag = threading.Event()
        # launch the thread
        audiothread = threading.Thread(
            target=clip.audio.preview,
            args=(audio_fps, audio_buffersize, audio_nbytes, audio_flag, video_flag),
        )
        audiothread.start()

    # passthrough to ffmpeg, passing flag for ffmpeg to set
    ffplay_preview_video(clip=clip, fps=fps, audio_flag=audio_flag, video_flag=video_flag)
