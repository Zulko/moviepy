from moviepy.decorators import (apply_to_mask, apply_to_audio,
                                 requires_duration)
from moviepy.video.compositing.concatenate import concatenate_videoclips
from .time_mirror import time_mirror

@requires_duration
@apply_to_mask
def time_symmetrize(clip):
    """
    Returns a clip that plays the current clip once forwards and
    then once backwards. This is very practival to make video that
    loop well, e.g. to create animated GIFs.
    This effect is automatically applied to the clip's mask and audio
    if they exist.
    """
    return concatenate_videoclips([clip, clip.fx( time_mirror )])
