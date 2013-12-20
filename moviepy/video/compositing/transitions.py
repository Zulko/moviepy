"""
Here is the current catalogue. These are meant
to be used with clip.fx. There are available as transfx.crossfadein etc.
if you load them with ``from moviepy.all import *``
"""

from moviepy.decorators import requires_duration, add_mask_if_none
from moviepy.video.fx import fadein, fadeout

@add_mask_if_none
def crossfadein(clip, duration):
	"""
	Makes the clip appear progressively, over ``duration`` seconds.
	Only works when the clip is included in a CompositeVideoClip.
	"""
	newclip = clip.copy()
	newclip.mask = clip.mask.fx(fadein, duration)
	return newclip


@requires_duration
@add_mask_if_none
def crossfadeout(clip, duration):
	"""
	Makes the clip disappear progressively, over ``duration`` seconds.
	Only works when the clip is included in a CompositeVideoClip.
	"""
	newclip = clip.copy()
	newclip.mask = clip.mask.fx(fadeout, duration)
	return newclip
