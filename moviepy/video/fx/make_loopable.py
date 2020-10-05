import moviepy.video.compositing.transitions as transfx
from moviepy.decorators import requires_duration
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip


@requires_duration
def make_loopable(clip, overlap_time):
    """
    Makes the clip fade in progressively at its own end, this way
    it can be looped indefinitely. ``overlap_time`` is the duration in seconds
    of the fade-in."""
    clip2 = clip.fx(transfx.crossfadein, overlap_time).with_start(
        clip.duration - overlap_time
    )
    return CompositeVideoClip([clip, clip2]).subclip(overlap_time, clip.duration)
