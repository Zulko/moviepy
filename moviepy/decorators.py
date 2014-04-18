"""
all decorators used in moviepy go there
"""

import decorator
from moviepy.tools import cvsecs



@decorator.decorator
def outplace(f, clip, *a, **k):
    """ Enables to make operations outplace """
    newclip = clip.copy()
    f(newclip, *a, **k)
    return newclip
    


@decorator.decorator
def apply_to_mask(f, clip, *a, **k):
    """ This decorator will apply the same function f to the mask of
        the clip created with f """
        
    newclip = f(clip, *a, **k)
    if hasattr(newclip, 'mask') and (newclip.mask != None):
        newclip.mask = f(newclip.mask, *a, **k)
    return newclip



@decorator.decorator
def apply_to_audio(f, clip, *a, **k):
    """ This decorator will apply the function f to the audio of
        the clip created with f """
        
    newclip = f(clip, *a, **k)
    if hasattr(newclip, 'audio') and (newclip.audio != None):
        newclip.audio = f(newclip.audio, *a, **k)
    return newclip
    
    

@decorator.decorator
def add_mask_if_none(f, clip, *a, **k):
    """ Add a mask to the clip if there is none. """
        
    if clip.mask is None:
        clip = clip.add_mask()
    return f(clip, *a, **k)



@decorator.decorator
def requires_duration(f, clip, *a, **k):
    """ Raise an error if the clip has no duration."""
    
    if clip.duration is None:
        raise ValueError("Attribute 'duration' not set")
    else:
        return f(clip, *a, **k)



@decorator.decorator
def audio_video_fx(f, clip, *a, **k):
    """ Use an audio function on a video/audio clip
    
    This decorator tells that the function f (audioclip -> audioclip)
    can be also used on a video clip, at which case it returns a
    videoclip with unmodified video and modified audio.
    """
    
    if hasattr(clip, "audio"):
        newclip = clip.copy()
        if clip.audio != None:
            newclip.audio =  f(clip.audio, *a, **k)
        return newclip
    else:
        return f(clip, *a, **k)



@decorator.decorator
def time_can_be_tuple(f, clip, *a, **k):
    """
    All tuples in the arguments of f will be considered as time and
    converted to seconds.
    """
    
    fun = lambda e: e if (not isinstance(e,tuple)) else cvsecs(*e)
    a = map(fun,a)
    k = dict( [(m, fun(n)) for m,n in k.items()])
    return f(clip, *a, **k)
