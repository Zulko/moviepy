def f_accel_decel(t, old_duration, new_duration, abruptness=1.0, soonness=1.0):
    """Acceleration and deceleration function.

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

    return old_duration * _f((t / new_duration) ** soonness)


def accel_decel(clip, new_duration=None, abruptness=1.0, soonness=1.0):
    """Accelerates and decelerates a clip, useful for GIF making.

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

    return clip.time_transform(
        lambda t: f_accel_decel(t, clip.duration, new_duration, abruptness, soonness)
    ).with_duration(new_duration)
