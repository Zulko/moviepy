from moviepy.decorators import audio_video_fx

@audio_video_fx
def volumex(clip, factor):
    """ Returns a clip with audio volume multiplied by the
    value `factor`. Can be applied to both audio and video clips.

    This effect is loaded as a clip method when you use moviepy.editor,
    so you can just write ``clip.volumex(2)``
    
    Examples
    ---------

    >>> newclip = volumex(clip, 2.0) # doubles audio volume
    >>> newclip = clip.fx( volumex, 0.5) # half audio, use with fx
    >>> newclip = clip.volumex(2) # only if you used "moviepy.editor"
    """ 
    return clip.fl(lambda gf, t: factor * gf(t),
    	           keep_duration = True)
