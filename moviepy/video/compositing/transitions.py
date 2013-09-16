"""
Don't abuse transitions ! Here is the current catalogue. These are meant
to be used with clip.fx 
"""

from moviepy.decorators import requires_duration

from moviepy.video.fx import fadein, fadeout

def crossfadein(clip, duration):
	"""
	Makes the clip appear progressively, over ``duration`` seconds.
	Only works when the clip is included in a CompositeVideoClip.
	"""
	newclip = clip.copy()
	newclip.mask = clip.mask.fx(fadein, duration)
	return newclip


@requires_duration
def crossfadeout(clip, duration):
	"""
	Makes the clip disappear progressively, over ``duration`` seconds.
	Only works when the clip is included in a CompositeVideoClip.
	"""
	newclip = clip.copy()
	newclip.mask = clip.mask.fx(fadeout, duration)
	return newclip
