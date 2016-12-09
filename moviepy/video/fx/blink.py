from copy import copy


def blink(clip, d_on, d_off, start=None, end=None):
    """
    Makes the clip blink. At each blink it will be displayed ``d_on``
    seconds and disappear ``d_off`` seconds. Will only work in
    composite clips.
    """
    newclip = copy(clip)

    if start is None:
        start = 0

    if newclip.mask is None:
        newclip = newclip.with_mask()

    D = d_on + d_off

    def fl_blink(gf, t):
        if t >= start and end and t <= end:
            return gf(t)*((t % D) < d_on)
        else:
            return gf(t)

    newclip.mask = newclip.mask.fl(fl_blink)

    return newclip
