from moviepy.Effect import Effect


class Scroll(Effect):
    """Effect that scrolls horizontally or vertically a clip, e.g. to make end credits

    Parameters
    ----------
    w, h
      The width and height of the final clip. Default to clip.w and clip.h

    x_speed, y_speed
      The speed of the scroll in the x and y directions.

    x_start, y_start
      The starting position of the scroll in the x and y directions.


    apply_to
      Whether to apply the effect to the mask too.
    """

    def __init__(
        self,
        w=None,
        h=None,
        x_speed=0,
        y_speed=0,
        x_start=0,
        y_start=0,
        apply_to="mask",
    ):

        self.w = w
        self.h = h
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.x_start = x_start
        self.y_start = y_start
        self.apply_to = apply_to

    def apply(self, clip):
        """Apply the effect to the clip."""
        if self.h is None:
            self.h = clip.h

        if self.w is None:
            self.w = clip.w

        x_max = self.w - 1
        y_max = self.h - 1

        def filter(get_frame, t):
            x = int(max(0, min(x_max, self.x_start + round(self.x_speed * t))))
            y = int(max(0, min(y_max, self.y_start + round(self.y_speed * t))))
            return get_frame(t)[y : y + self.h, x : x + self.w]

        return clip.transform(filter, apply_to=self.apply_to)
