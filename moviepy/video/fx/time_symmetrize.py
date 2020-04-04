from moviepy.decorators import requires_duration


@requires_duration
def time_symmetrize(clip):
    """
    Returns a clip that plays the current clip once forwards and
    then once backwards. This is very practival to make video that
    loop well, e.g. to create animated GIFs.
    This effect is automatically applied to the clip's mask and audio
    if they exist.
    """
    return clip + clip[::-1]
