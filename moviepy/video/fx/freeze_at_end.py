from moviepy.decorators import requires_duration
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip


@requires_duration
def freeze_at_end(clip, freeze_duration=None,
                  total_duration=None, delta=0.05):
    """
    Makes the clip freeze on its last frame.  With ``duration`` you can
    specify the duration of the freeze. With ``total_duration`` you can
    specify the total duration of the clip and the freeze (i.e. the
    duration of the freeze is automatically calculated). If neither
    is provided, the freeze will have an infinite length.
    
    The clip is frozen on the frame at time (clip.duration - delta)
    """
    
    freezed_clip = ImageClip(clip.get_frame(clip.end - delta))
    if total_duration:
        freeze_duration = total_duration - clip.duration
    if freeze_duration:
        freezed_clip = freezed_clip.set_duration(freeze_duration)
    
    return CompositeVideoClip([clip,freezed_clip.set_start(clip.end)])
