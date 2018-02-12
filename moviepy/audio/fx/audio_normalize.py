from moviepy.decorators import audio_video_fx

@audio_video_fx
def audio_normalize(clip):
    """ Return an audio (or video) clip whose volume is normalized
        to 0db."""

    mv = clip.max_volume()
    return clip.volumex(1 / mv)
