from moviepy.decorators import requires_duration, apply_to_mask, apply_to_audio


@requires_duration
@apply_to_mask
@apply_to_audio
def time_mirror(clip):
    """
    Returns a clip that plays the current clip backwards.
    The clip must have its ``duration`` attribute set.
    The same effect is applied to the clip's audio and mask if any.
    """
    return clip[::-1]
