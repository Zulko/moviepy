from moviepy.decorators import audio_video_fx

@audio_video_fx
def volumex(clip, factor):
    """ Returns a (video or audio) clip with increased sound volume """ 
    return clip.fl(lambda gf, t: factor * gf(t), keep_duration = True)
