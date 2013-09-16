from moviepy.decorators import (apply_to_mask,
                                 apply_to_audio,
                                 requires_duration)


@requires_duration
@apply_to_mask
@apply_to_audio
def loop(self):
	"""
	Returns a clip that plays the current clip in an infinite loop.
	Ideal for clips coming from gifs.
	"""
	return self.fl_time(lambda t: t % self.duration)
