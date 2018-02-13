from moviepy.decorators import (apply_to_mask,
                                 apply_to_audio,
                                 requires_duration)


@requires_duration
@apply_to_mask
@apply_to_audio
def loop(self, n=None, duration=None):
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
    result = self.fl_time(lambda t: t % self.duration)
    if n:
        duration = n*self.duration
    if duration:
        result = result.set_duration(duration)
    return result
