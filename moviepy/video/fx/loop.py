from moviepy.decorators import requires_duration


@requires_duration
def loop(clip, n=None, duration=None):
    """
    Returns a clip that plays the current clip in an infinite loop.
    Ideal for clips coming from GIFs.

    Parameters
    ----------

    n
      Number of times the clip should be played. If `None` the
      the clip will loop indefinitely (i.e. with no set duration).

    duration
      Total duration of the clip. Can be specified instead of n.
    """
    previous_duration = clip.duration
    clip = clip.time_transform(
        lambda t: t % previous_duration, apply_to=["mask", "audio"]
    )
    if n:
        duration = n * previous_duration
    if duration:
        clip = clip.with_duration(duration)
    return clip
