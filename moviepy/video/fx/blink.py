import copy


def blink(clip, duration_on, duration_off):
    """
    Makes the clip blink. At each blink it will be displayed ``duration_on``
    seconds and disappear ``duration_off`` seconds. Will only work in
    composite clips.
    """
    newclip = copy.copy(clip)
    if newclip.mask is None:
        newclip = newclip.with_mask()
    duration = duration_on + duration_off
    newclip.mask = newclip.mask.with_filter(lambda get_frame, t: get_frame(t) * ((t % duration) < duration_on))
    return newclip
