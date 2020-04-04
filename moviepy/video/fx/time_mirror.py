from moviepy.decorators import requires_duration


@requires_duration
def time_mirror(self):
    """
    Returns a clip that plays the current clip backwards.
    The clip must have its ``duration`` attribute set.
    The same effect is applied to the clip's audio and mask if any.
    """
    return self[::-1]
