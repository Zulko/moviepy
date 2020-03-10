from moviepy.decorators import apply_to_audio, apply_to_mask


def speedx(clip, factor = None, final_duration=None):
    """
    Returns a clip playing the current clip but at a speed multiplied
    by ``factor``. Instead of factor one can indicate the desired
    ``final_duration`` of the clip, and the factor will be automatically
    computed.
    The same effect is applied to the clip's audio and mask if any.
    """
    
    if final_duration:
        factor = 1.0* clip.duration / final_duration
        
    newclip = clip.fl_time(lambda t: factor * t, apply_to=['mask', 'audio'])
    
    if clip.duration is not None:
        newclip = newclip.set_duration(1.0 * clip.duration / factor)
    
    return newclip
