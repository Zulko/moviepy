from moviepy.decorators import apply_to_audio, apply_to_mask, requires_duration


@requires_duration
@apply_to_mask
@apply_to_audio
def time_mirror(self):
    """
    Returns a clip that plays the current clip backwards.
    The clip must have its ``duration`` attribute set.
    The same effect is applied to the clip's audio and mask if any.
    """
    return self.fl_time(lambda t: self.duration - t, keep_duration=True)
