from moviepy.decorators import audio_video_fx, requires_duration
import numpy as np

@audio_video_fx
@requires_duration
def audio_fadeout(clip, duration):
    """ Return a sound clip where the sound fades out progressively
        over ``duration`` seconds at the end of the clip. """
    
    def fading(gf,t):
        gft = gf(t)
        
        if np.isscalar(t):
            factor = min(1.0 * (clip.duration - t) / duration, 1)
            factor = np.array([factor,factor])
        else:
            factor = np.minimum( 1.0 * (clip.duration - t) / duration, 1)
            factor = np.vstack([factor,factor]).T
        return factor * gft
    
    return clip.fl(fading, keep_duration = True)
