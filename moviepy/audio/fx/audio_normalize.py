from moviepy.audio.fx.multiply_volume import multiply_volume
from moviepy.decorators import audio_video_fx


@audio_video_fx
def audio_normalize(clip):
    """Return a clip whose volume is normalized to 0db.

    Return an audio (or video) clip whose audio volume is normalized
    so that the maximum volume is at 0db, the maximum achievable volume.

    Examples
    --------

    >>> from moviepy import *
    >>> videoclip = VideoFileClip('myvideo.mp4').fx(afx.audio_normalize)

    """
    max_volume = clip.max_volume()
    if max_volume == 0:
        # Nothing to normalize.
        # Avoids a divide by zero error.
        return clip.copy()
    else:
        return multiply_volume(clip, 1 / max_volume)
