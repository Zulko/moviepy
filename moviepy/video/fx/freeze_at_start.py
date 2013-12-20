from moviepy.decorators import requires_duration
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.concatenate import concatenate


@requires_duration
def freeze_at_start(clip, freeze_duration=None, total_duration=None):
    """
    Makes the clip freeze on its last frame.  With ``duration`` you can
    specify the duration of the freeze. With ``total_duration`` you can
    specify the total duration of the clip and the freeze (i.e. the
    duration of the freeze is automatically calculated). If neither
    is provided, the freeze will have an infinite length.
    """
    
    freezed_clip = ImageClip(clip.get_frame(0))
    if total_duration:
        freeze_duration = total_duration - clip.duration
    if freeze_duration:
        freezed_clip = freezed_clip.set_duration(freeze_duration)
    
    return concatenate([freezed_clip,clip])
