from moviepy.decorators import apply_to_mask,apply_to_audio

@apply_to_mask
@apply_to_audio
def speedx(self, factor):
	"""
	Returns a clip playing the current clip but at a speed multiplied
	by ``factor``.
	The same effect is applied to the clip's audio and mask if any.
	"""
	newclip = self.fl_time(lambda t: factor * t)
	if self.duration != None:
		return newclip.set_duration(1.0 * self.duration / factor)
	else:
		return newclip
