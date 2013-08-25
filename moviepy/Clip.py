import decorator
from copy import copy, deepcopy


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
def requires_duration(f, clip, *a, **k):
    """ will raise an error if the clip has no duration."""
    if clip.duration is None:
        raise ValueError("Attribute 'duration' not set")
    else:
        return f(clip, *a, **k)


#
#
#                         C L I P
#
#


class Clip:

    """
        
     Base class of all clips (VideoClips and AudioClips).
      
       
           
     :ivar start: When the clip is included in a composition, time of the
         composition at which the clip starts playing (in seconds). 
     
     :ivar end: When the clip is included in a composition, time of the
         composition at which the clip starts playing (in seconds).
     
     :ivar duration: duration of the clip (in seconds). Some clips
         are infinite and do not have any duration.
     
     """

    def __init__(self):

        self.start = 0
        self.end = None
        self.duration = None

    def fl(self, fl, applyto=[], keep_duration=True):
        """
        Returns a clip whose frames are a transformation (through ``fl``)
        of the frames of the current clip.
        
        :param fl: a function with signature (gf,t -> frame) where:
           - `gf` is a clip ``get_frame`` method, i.e. a function (t->image).
           - `t` is a time in seconds
           - `frame` is a picture (=Numpy array), and is the frame of the
              returned clip at time ``t``.
           
        :param applyto: can be either 'mask', or 'audio', or ['mask','audio'].
           Specifies if the filter ``fl`` should also be applied to the
           audio or the mask of the clip, if any.
        
        :param keep_duration: Should the attributes ``duration`` and ``end``
              of the clip be discarded.
        
        >>> # ``newclip``, made from ``clip``, will be a 100 pixels-high
        >>> # whose video content scrolls from the top to the bottom of
        >>> # the frames of ``clip``.
        >>> fl = lambda gf,t : gf(t)[int(t):int(t)+50,:]
        >>> newclip = clip.fl(fl,applyto='mask')
        
        """

        gf = copy(self.get_frame)
        newclip = self.set_get_frame(lambda t: fl(gf, t))
        
        if not keep_duration:
			newclip.duration = None
			newclip.end = None
			
        if isinstance(applyto, str):
            applyto = [applyto]

        for attr in applyto:
            if hasattr(newclip, attr):
                a = getattr(newclip, attr)
                if a != None:
                    setattr(newclip, attr, a.fl(fl))
                    
        return newclip

    def fl_time(self, t_func, applyto=['mask', 'sound'], keep_duration=False):
        """
        Returns a clip playing the content of the current clip but with a
        modified timeline, time ``t`` being replaced by another
        time `t_func(t)`. By default the attributes ``duration`` and ``end``
        of the returned clip are discarded.
        
        :param applyto: can be either 'mask', or 'audio', or ['mask','audio'].
           Specifies if the filter ``fl`` should also be applied to the
           audio or the mask of the clip, if any.
        
        :param keep_duration: Should the attributes ``duration`` and ``end``
              of the clip be discarded.
        
        >>> # plays the clip (and its mask and sound) twice faster
        >>> newclip = clip.fl_time(lambda: 2*t, applyto=['mask','audio'])
        >>>
        >>> # plays the clip starting at t=3, and backwards:
        >>> newclip = clip.fl_time(lambda: 3-t)
        
        """
        
        return self.fl(lambda gf, t: gf(t_func(t)), applyto,
                                    keep_duration=keep_duration)

    @apply_to_mask
    @apply_to_audio
    def set_start(self, t):
        """
        Returns a copy of the clip, with the ``start`` attribute set to ``t``.
        Also sets the duration of the returned clip's mask and audio, if any.
        """
        newclip = copy(self)
        newclip.start = t
        if newclip.end is None:
            if newclip.duration != None:
                newclip.end = t + newclip.duration
        else:
            newclip.duration = newclip.end - newclip.start

        return newclip

    @apply_to_mask
    @apply_to_audio
    def set_end(self, t):
        """
        Returns a copy of the clip, with the ``end`` attribute set to ``t``.
        Also sets the duration of the returned clip's mask and audio, if any.
        """
        newclip = copy(self)
        newclip.end = t
        if newclip.start is None:
            if newclip.duration != None:
                newclip.start = max(0, t - newclip.duration)
        else:
            newclip.duration = newclip.end - newclip.start

        return newclip

    @apply_to_mask
    @apply_to_audio
    def set_duration(self, t):
        """
        Returns a copy of the clip, with the  ``duration`` attribute set
        to ``t``.
        Also sets the duration of the returned clip's mask and audio, if any.
        """
        newclip = copy(self)
        newclip.duration = t
        if (newclip.start is None):
            if newclip.end != None:
                newclip.start = max(0, newclip.end - t)
        else:
            newclip.end = newclip.start + t
            
        return newclip

    def set_get_frame(self, gf):
        newclip = copy(self)
        newclip.get_frame = gf
        return newclip

    def is_playing(self, t):
        """
        Return true if t is between the start and the end of the clip """
        return (((self.end is None) and (t >= self.start)) or
                (self.start <= t <= self.end))
    
    @apply_to_mask
    @apply_to_audio
    def subclip(self, ta=0, tb=None):
        """
        Returns a clip playing the content of the current clip
        between times ``ta`` and ``tb`` (in seconds). If tb is not
        provided, plays until the end of the clip, potentially forever.
        If ``tb`` is provided, the duration of the returned clip is
        set automatically.
        The same effect is applied to the clip's audio and mask if any.
        """
        newclip = self.fl_time(lambda t: t + ta)
        if (tb != None):
            return newclip.set_duration(tb - ta)
        else:
            return newclip

    @apply_to_mask
    @apply_to_audio
    def cutout(self, ta, tb):
        """
        Returns a clip playing the content of the current clip but
        skips the extract between ``ta`` and ``tb`` (in seconds).
        If the original clip clip has a ``duration`` attribute set,
        the returned clip's duration is automatically computed.
        The same effect is applied to the clip's audio and mask if any.
        """
        fl = lambda t: t + (0 if (t < ta) else tb - ta)
        newclip = self.fl_time(fl)
        if self.duration != None:
            return newclip.set_duration(self.duration - (tb - ta))
        else:
            return newclip

    @requires_duration
    @apply_to_mask
    @apply_to_audio
    def time_mirror(self):
        """
        Returns a clip that plays the current clip backwards (who said
        useless ???). The clip must have its ``duration`` attribute set.
        The same effect is applied to the clip's audio and mask if any.
        """
        return self.fl_time(lambda t: self.duration - t)
    
    @requires_duration
    @apply_to_mask
    @apply_to_audio
    def loop(self):
        """
        Returns a clip that plays the current clip in an infinite loop.
        """
        return self.fl_time(lambda t: t % self.duration)	
        
    @apply_to_mask
    @apply_to_audio
    def speedx(self, factor):
        """
        Returns a clip playing the current clip but at a speed multiplied
        by ``factor``.
        The same effect is applied to the clip's audio and mask if any.
        """
        newclip = self.fl_time(lambda t: factor * t)
        if self.duration != None:
            return newclip.set_duration(1.0 * self.duration / factor)
        else:
            return newclip
