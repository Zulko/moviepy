import moviepy.video.compositing.transitions as transfx
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip


def make_loopable(clip, cross):
    """
    Makes the clip fade in progressively at its own end, this way
    it can be looped indefinitely. ``cross`` is the duration in seconds
    of the fade-in.  """  
    d = clip.duration
    clip2 = clip.fx(transfx.crossfadein, cross).\
                 set_start(d - cross)
    return CompositeVideoClip([ clip, clip2 ]).\
                 subclip(cross,d)
