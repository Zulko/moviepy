from moviepy.decorators import audio_video_fx

from .volumex import volumex


@audio_video_fx
def audio_normalize(clip):
    """ Return a clip whose volume is normalized to 0db.

    Return an audio (or video) clip whose audio volume is normalized
    so that the maximum volume is at 0db, the maximum achievable volume.

    Examples
    ========

    >>> from moviepy.editor import *
    >>> videoclip = VideoFileClip('myvideo.mp4').fx(afx.audio_normalize)

    """


    mv = clip.max_volume()
    return volumex(clip, 1 / mv)
