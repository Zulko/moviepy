def blink(clip, d_on, d_off):
    """
    Makes the clip blink. At each blink it will be displayed ``d_on``
    seconds and disappear ``d_off`` seconds. Will only work in
    composite clips.
    """
    newclip = copy(clip)
    if newclip.mask is None:
        newclip = newclip.with_mask()
    D = d_on + d_off
    newclip.mask = newclip.mask.fl( lambda gf,t: gf(t)*((t % D) < d_on))
    return newclip
