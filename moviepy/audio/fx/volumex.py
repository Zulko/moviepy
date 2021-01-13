from moviepy.decorators import audio_video_fx


@audio_video_fx
def volumex(clip, factor):
    """Returns a clip with audio volume multiplied by the
    value `factor`. Can be applied to both audio and video clips.

    This effect is loaded as a clip method so you can just write ``clip.volumex(2)``

    Examples
    ---------

    >>> new_clip = volumex(clip, 2.0) # doubles audio volume
    >>> new_clip = clip.fx( volumex, 0.5) # half audio, use with fx
    >>> new_clip = clip.volumex(2)
    """
    return clip.transform(
        lambda get_frame, t: factor * get_frame(t), keep_duration=True
    )
