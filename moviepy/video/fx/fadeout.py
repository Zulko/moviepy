from moviepy.decorators import requires_duration

@requires_duration
def fadeout(clip, duration):
    """
    Makes the clip fade to black progressively, over ``duration`` seconds.
    For more advanced fading, see ``composition.crossfade``
    """
    fading = lambda t: min(1.0 * (clip.duration - t) / duration, 1)
    return clip.fl(lambda gf, t: fading(t) * gf(t))


    

                     
