def f_accel_decel(t, old_d, new_d, abruptness=1.0, soonness=1.0):
    """
    abruptness
      negative abruptness (>-1): speed up down up
      zero abruptness : no effect
      positive abruptness: speed down up down

    soonness
      for positive abruptness, determines how soon the
      speedup occurs (0<soonness < inf)
    """

    a = 1.0 + abruptness

    def _f(t):
        def f1(t):
            return (0.5) ** (1 - a) * (t ** a)

        def f2(t):
            return 1 - f1(1 - t)

        return (t < 0.5) * f1(t) + (t >= 0.5) * f2(t)

    return old_d * _f((t / new_d) ** soonness)


def accel_decel(clip, new_duration=None, abruptness=1.0, soonness=1.0):
    """

    new_duration
      If None, will be that of the current clip.

    abruptness
      negative abruptness (>-1): speed up down up
      zero abruptness : no effect
      positive abruptness: speed down up down

    soonness
      for positive abruptness, determines how soon the
      speedup occurs (0<soonness < inf)
    """

    if new_duration is None:
        new_duration = clip.duration

    return clip.fl_time(
        lambda t: f_accel_decel(t, clip.duration, new_duration, abruptness, soonness)
    ).set_duration(new_duration)
