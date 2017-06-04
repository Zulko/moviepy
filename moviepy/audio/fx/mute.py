from moviepy.decorators import audio_video_fx

@audio_video_fx
def mute(clip):
    """ Returns a clip with no audio volume . Can be applied to both
        audio and video clips. This effect is loaded as a clip method
        when you use moviepy.editor,so you can just write
        ``clip.volumex(2)``

    Examples
    ---------
    >>> newclip = mute(clip)
    >>> newclip = clip.fx(mute) # half audio, use with fx
    """
    return clip.fl(lambda gf, t: 0 * gf(t),
    	           keep_duration = True)
