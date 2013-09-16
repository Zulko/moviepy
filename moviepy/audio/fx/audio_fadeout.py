from moviepy.decorators import audio_video_fx, requires_duration

@audio_video_fx
@requires_duration
def audio_fadeout(self, duration):
    """ Return a sound clip where the sound fades out progressively
        over ``duration`` seconds at the end of the clip. """
    fading = lambda gf, t: max(
        1.0 * (self.duration - t) / duration, 0) * gf(t)
    return self.fl(fading, keep_duration = True)
