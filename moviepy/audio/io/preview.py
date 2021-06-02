"""Audio preview functions for MoviePy editor."""

import time

import numpy as np
import pygame as pg

from moviepy.decorators import requires_duration


pg.init()
pg.display.set_caption("MoviePy")


@requires_duration
def preview(
    clip, fps=22050, buffersize=4000, nbytes=2, audio_flag=None, video_flag=None
):
    """
    Plays the sound clip with pygame.

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
    pg.mixer.quit()

    pg.mixer.init(fps, -8 * nbytes, clip.nchannels, 1024)
    totalsize = int(fps * clip.duration)
    pospos = np.array(list(range(0, totalsize, buffersize)) + [totalsize])
    timings = (1.0 / fps) * np.arange(pospos[0], pospos[1])
    sndarray = clip.to_soundarray(timings, nbytes=nbytes, quantize=True)
    chunk = pg.sndarray.make_sound(sndarray)

    if (audio_flag is not None) and (video_flag is not None):
        audio_flag.set()
        video_flag.wait()

    channel = chunk.play()
    for i in range(1, len(pospos) - 1):
        timings = (1.0 / fps) * np.arange(pospos[i], pospos[i + 1])
        sndarray = clip.to_soundarray(timings, nbytes=nbytes, quantize=True)
        chunk = pg.sndarray.make_sound(sndarray)
        while channel.get_queue():
            time.sleep(0.003)
            if video_flag is not None:
                if not video_flag.is_set():
                    channel.stop()
                    del channel
                    return
        channel.queue(chunk)
