from moviepy.decorators import audio_video_fx
import numpy as np


@audio_video_fx
def audio_levels(clip, levels, fast=False):
    """ Return an audio clip (or video) by leveling
        the audio with the received array.

        clip = clip.fx(audio_levels,
                       levels=[(0, 1), (5, 0), (10, 1)],
                       fast=True)  # fast is imprecise
    """

    def level(gf, t):
        def get_range_levels(t):
            ant = levels[0]
            sig = None

            for l in levels:
                if l[0] <= t:
                    ant = l
                else:
                    sig = l
                    break
            if not sig:  # hack time
                sig = ant[0] + 1, ant[1]
            return ant, sig

        def scalar(t):
            gft = gf(t)
            ant, sig = get_range_levels(t)

            pos = (t - ant[0]) / (sig[0] - ant[0])
            factor = pos * sig[1] + (1 - pos) * ant[1]
            return np.array([factor, factor]) * gft

        def not_scalar_fast(t):
            gft = gf(t)
            ant, sig = get_range_levels(t[0])

            pos = (t - ant[0]) / (sig[0] - ant[0])
            factor = pos * sig[1] + (1 - pos) * ant[1]
            return np.vstack([factor, factor]).T * gft

        def not_scalar(t):
            gft = gf(t)
            ant, sig = get_range_levels(t[0])

            for it in range(len(t)):
                if sig[0] <= t[it]:
                    ant, sig = get_range_levels(t[it])

                pos = (t[it] - ant[0]) / (sig[0] - ant[0])
                factor = pos * sig[1] + (1 - pos) * ant[1]
                gft[it] *= np.array([factor, factor])
            return gft

        if np.isscalar(t):
            return scalar(t)
        if fast:
            return np.array(not_scalar_fast(t))
        return np.array(not_scalar(t))

    return clip.fl(level, keep_duration=True)
