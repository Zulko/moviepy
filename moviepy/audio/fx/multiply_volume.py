from moviepy.decorators import audio_video_fx


@audio_video_fx
def multiply_volume(clip, factor):
    """Returns a clip with audio volume multiplied by the
    value `factor`. Can be applied to both audio and video clips.

    This effect is loaded as a clip method when you use moviepy.editor,
    so you can just write ``clip.multiply_volume(2)``

    Examples
    --------

    >>> from moviepy import AudioFileClip
    >>> music = AudioFileClip('music.ogg')
    >>> new_clip = clip.multiply_volume(2)  # doubles audio volume
    >>> new_clip = clip.multiply_volume(0.5)  # half audio
    """
    return clip.transform(
        lambda get_frame, t: factor * get_frame(t), keep_duration=True
    )
