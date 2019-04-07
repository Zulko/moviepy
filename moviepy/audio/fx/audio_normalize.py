from moviepy.decorators import audio_video_fx
from .volumex import volumex

@audio_video_fx
def audio_normalize(clip):
    """ Return an audio (or video) clip whose volume is normalized
        to 0db."""

    mv = clip.max_volume()
    return volumex(clip, 1 / mv)
