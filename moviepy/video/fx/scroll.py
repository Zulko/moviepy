def scroll(
    clip, h=None, w=None, x_speed=0, y_speed=0, x_start=0, y_start=0, apply_to="mask"
):
    """ Scrolls horizontally or vertically a clip, e.g. to make end
        credits """
    if h is None:
        h = clip.h
    if w is None:
        w = clip.w

    x_max = clip.w - w - 1
    y_max = clip.h - h - 1

    def filter(get_frame, t):
        x = int(max(0, min(x_max, x_start + round(x_speed * t))))
        y = int(max(0, min(y_max, y_start + round(y_speed * t))))
        return get_frame(t)[y : y + h, x : x + w]

    return clip.with_filter(filter, apply_to=apply_to)
