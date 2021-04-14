import numpy as np

from moviepy.decorators import audio_video_fx, requires_duration


@audio_video_fx
@requires_duration
def audio_fadeout(clip, duration):
    """Return a sound clip where the sound fades out progressively
    over ``duration`` seconds at the end of the clip.
    """

    def fading(get_frame, t):
        frame = get_frame(t)

        if np.isscalar(t):
            factor = min(1.0 * (clip.duration - t) / duration, 1)
            factor = np.array([factor, factor])
        else:
            factor = np.minimum(1.0 * (clip.duration - t) / duration, 1)
            factor = np.vstack([factor, factor]).T
        return factor * frame

    return clip.transform(fading, keep_duration=True)
