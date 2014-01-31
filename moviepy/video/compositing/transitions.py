"""
Here is the current catalogue. These are meant
to be used with clip.fx. There are available as transfx.crossfadein etc.
if you load them with ``from moviepy.all import *``
"""

from moviepy.decorators import requires_duration, add_mask_if_none
from .CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout

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










@requires_duration
def make_loopable(clip, cross_duration):
    """ Makes the clip fade in progressively at its own end, this way
    it can be looped indefinitely. ``cross`` is the duration in seconds
    of the fade-in.  """  
    d = clip.duration
    clip2 = clip.fx(crossfadein, cross_duration).\
                 set_start(d - cross_duration)
    return CompositeVideoClip([ clip, clip2 ]).\
                 subclip(cross_duration,d)
