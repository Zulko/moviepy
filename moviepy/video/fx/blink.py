def blink(clip, duration_on, duration_off):
    """
    Makes the clip blink. At each blink it will be displayed ``duration_on``
    seconds and disappear ``duration_off`` seconds. Will only work in
    composite clips.
    """
    new_clip = clip.copy()
    if new_clip.mask is None:
        new_clip = new_clip.with_mask()
    duration = duration_on + duration_off
    new_clip.mask = new_clip.mask.transform(
        lambda get_frame, t: get_frame(t) * ((t % duration) < duration_on)
    )
    return new_clip
