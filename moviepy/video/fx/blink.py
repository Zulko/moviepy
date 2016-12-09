from copy import copy


def blink(clip, d_on, d_off, start=None, end=None):
    """
    Makes the clip blink. At each blink it will be displayed ``d_on``
    seconds and disappear ``d_off`` seconds. Will only work in
    composite clips.
    """
    newclip = copy(clip)

    if newclip.mask is None:
        newclip = newclip.with_mask()

    period = d_on + d_off

    def fl_blink(gf, t):
        if (start is None or t >= start) and (end is None or t <= end):
            return gf(t)*((t % period) < d_on)
        else:
            return gf(t)

    newclip.mask = newclip.mask.fl(fl_blink)

    return newclip
