from moviepy.decorators import apply_to_mask,apply_to_audio
from moviepy.audio.fx.time_stretch import time_stretch

def speedx(clip, factor = None, final_duration=None, stretch_audio=False):
    """
    Returns a clip playing the current clip but at a speed multiplied
    by ``factor``. Instead of factor one can indicate the desired
    ``final_duration`` of the clip, and the factor will be automatically
    computed.
    The same effect is applied to the clip's audio and mask if any.
    """

    if final_duration:
        factor = 1.0* clip.duration / final_duration

    newclip = clip.fl_time(lambda t: factor * t, apply_to=['mask', 'audio'])

    if clip.duration is not None:
        newclip = newclip.set_duration(1.0 * clip.duration / factor)

    if stretch_audio:
        stretched_audio = time_stretch(clip.audio, factor)
        stretched_audio.duration = newclip.duration
        newclip = newclip.set_audio(stretched_audio)

    return newclip
