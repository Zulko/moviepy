from moviepy.decorators import (apply_to_mask,
                                 apply_to_audio,
                                 requires_duration)


@requires_duration
@apply_to_mask
@apply_to_audio
def loop(self, n=None):
    """
    Returns a clip that plays the current clip in an infinite loop.
    Ideal for clips coming from gifs.
    :param n: number of times the clip should be played. If `None` the
        the clip will loop indefinitely (i.e. with no set duration).
    """
    result = self.fl_time(lambda t: t % self.duration)
    if n:
        result.duration = n*self.duration
    return result
