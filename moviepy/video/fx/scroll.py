def scroll(
    clip, w=None, h=None, x_speed=0, y_speed=0, x_start=0, y_start=0, apply_to="mask"
):
    """
    Scrolls horizontally or vertically a clip, e.g. to make end credits

    Parameters
    -----------

    w, h
      The width and height of the final clip. Default to clip.w and clip.h

    x_speed, y_speed

    x_start, y_start


    apply_to

    """
    if h is None:
        h = clip.h
    if w is None:
        w = clip.w

    xmax = clip.w - w - 1
    ymax = clip.h - h - 1

    def f(gf, t):
        x = int(max(0, min(xmax, x_start + round(x_speed * t))))
        y = int(max(0, min(ymax, y_start + round(y_speed * t))))
        return gf(t)[y : y + h, x : x + w]

    return clip.fl(f, apply_to=apply_to)
