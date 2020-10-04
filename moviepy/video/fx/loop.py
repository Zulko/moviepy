from moviepy.decorators import apply_to_audio, apply_to_mask, requires_duration


@requires_duration
@apply_to_mask
@apply_to_audio
def loop(clip, n=None, duration=None):
    """
    Returns a clip that plays the current clip in an infinite loop.
    Ideal for clips coming from gifs.

    Parameters
    ------------
    n
      Number of times the clip should be played. If `None` the
      the clip will loop indefinitely (i.e. with no set duration).

    duration
      Total duration of the clip. Can be specified instead of n.
    """
    previous_duration = clip.duration
    clip = clip.fl_time(lambda t: t % previous_duration)
    if n:
        duration = n * previous_duration
    if duration:
        clip = clip.set_duration(duration)
    return clip
