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
    def get_range_levels(t):
        if t >= cache['prv'][0] and t < cache['nxt'][0]:
            return cache['prv'], cache['nxt'], cache['final']
        elif t >= cache['nxt'][0] and cache['final']:
            # final point not defined
            return cache['prv'], cache['nxt'], cache['final']

        match_next = False
        for l in levels:
            if l[0] <= t:
                cache['prv'] = l
            else:
                cache['nxt'] = l
                match_next = True
                break
        if not match_next:
            cache['nxt'] = cache['prv'][0] + 1, cache['prv'][1]
            cache['final'] = True

        elif cache['prv'] == cache['nxt']:
            # init point not defined
            cache['prv'] = cache['prv'][0] - 1, cache['prv'][1]

        return cache['prv'], cache['nxt'], cache['final']

    def level(gf, t):
        def scalar(t):
            gft = gf(t)
            prv, nxt, final = get_range_levels(t)

            pos = (t - prv[0]) / (nxt[0] - prv[0])
            factor = pos * nxt[1] + (1 - pos) * prv[1]
            return np.array([factor, factor]) * gft

        def not_scalar_fast(t, prv=False, nxt=False):
            gft = gf(t)

            if not prv or not nxt:
                prv, nxt, final = get_range_levels(t[0])

            pos = (t - prv[0]) / (nxt[0] - prv[0])
            factor = pos * nxt[1] + (1 - pos) * prv[1]
            return np.vstack([factor, factor]).T * gft

        def not_scalar(t):
            gft = gf(t)
            prv, nxt, final = get_range_levels(t[0])

            if t[-1] < nxt[0] or final:
                return not_scalar_fast(t, prv, nxt)

            for it in range(len(t)):
                if t[it] >= nxt[0] and not final:
                    prv, nxt, final = get_range_levels(t[it])

                pos = (t[it] - prv[0]) / (nxt[0] - prv[0])
                factor = pos * nxt[1] + (1 - pos) * prv[1]
                gft[it] *= np.array([factor, factor])
            return gft

        if np.isscalar(t):
            return scalar(t)
        if fast:
            return np.array(not_scalar_fast(t))
        return np.array(not_scalar(t))

    cache = {'prv': levels[0], 'nxt': levels[0], 'final': False}
    get_range_levels(0)
    return clip.fl(level, keep_duration=True)
