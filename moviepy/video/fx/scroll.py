def scroll(clip, h=None, w=None, x_speed=0, y_speed=0,
           x_start=0, y_start=0, apply_to="mask",
           ease_func=None, period=1):
    """ Scrolls horizontally or vertically a clip, e.g. to make end
        credits """
    if h is None: h = clip.h
    if w is None: w = clip.w
    
    xmax = clip.w-w-1
    ymax = clip.h-h-1

    def f(gf,t):
        if ease_func and t < period:
            t = ease_func(t, duration=period) * period
        x = int(max(0, min(xmax, x_start+ round(x_speed*t))))
        y = int(max(0, min(ymax, y_start+ round(y_speed*t))))
        return gf(t)[y:y+h, x:x+w]
    
    return clip.fl(f, apply_to = apply_to)
