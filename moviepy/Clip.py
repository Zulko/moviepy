"""
This module implements the central object of MoviePy, the Clip, and
all the methods that are common to the two subclasses of Clip, VideoClip
and AudioClip.
"""

from copy import copy
import numpy as np

from moviepy.decorators import ( apply_to_mask, apply_to_audio,
                                   time_can_be_tuple)


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
    
    # prefix for all tmeporary video and audio files.
    # You can overwrite it with 
    # >>> Clip._TEMP_FILES_PREFIX = "temp_"
    
    _TEMP_FILES_PREFIX = 'TEMP_MPY_'

    def __init__(self):

        self.start = 0
        self.end = None
        self.duration = None
        
    def copy(self):
        return copy(self)

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

    
    def fl_time(self, t_func, applyto=[], keep_duration=False):
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
    
    def fx(self, func, *args, **kwargs):
        """
        
        Returns the result of ``func(self, *args, **kwargs)``.
        for instance
        
        >>> newclip = clip.fx(resize,0.2,method='bilinear')
        
        is equivalent to
        
        >>> newclip = resize(clip,0.2, method='bilinear')
        
        The motivation of fx is to keep the name of the effect near its
        parameters, when the effects are chained:
        
        >>> from moviepy.fx import volumex, resize, mirrorx
        >>> clip.fx( volumex, 0.5).fx( resize, 0.3).fx( mirrorx )
        >>> # Is equivalent, but clearer than
        >>> resize( volumex( mirrorx( clip ), 0.5), 0.3)
        
        """
        
        return func(self, *args, **kwargs)
            

    @apply_to_mask
    @apply_to_audio
    @time_can_be_tuple
    def set_start(self, t, change_end=True):
        """
        Returns a copy of the clip, with the ``start`` attribute set to ``t``.
        Automatically changes the end of the clip if the clip has a duration
        and ``change_end`` is True. Else, sets the duration of the
        returned clip's mask and audio, if any.
        """
        newclip = self.copy()
        newclip.start = t
        if (newclip.duration != None) and change_end:
            newclip.end = t + newclip.duration
        elif (newclip.end !=None):
            newclip.duration = newclip.end - newclip.start

        return newclip

    @apply_to_mask
    @apply_to_audio
    @time_can_be_tuple
    def set_end(self, t):
        """
        Returns a copy of the clip, with the ``end`` attribute set to ``t``.
        Also sets the duration of the returned clip's mask and audio, if any.
        """
        newclip = self.copy()
        newclip.end = t
        if newclip.start is None:
            if newclip.duration != None:
                newclip.start = max(0, t - newclip.duration)
        else:
            newclip.duration = newclip.end - newclip.start

        return newclip

    @apply_to_mask
    @apply_to_audio
    @time_can_be_tuple
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
    
    @time_can_be_tuple
    def is_playing(self, t):
        """
        Return true if t is between the start and the end of the clip """
        if isinstance(t, np.ndarray):
            t = t.max()
        return (((self.end is None) and (t >= self.start)) or
                (self.start <= t <= self.end))
    
    @time_can_be_tuple
    @apply_to_mask
    @apply_to_audio
    def subclip(self, ta=0, tb=None):
        """
        Returns a clip playing the content of the current clip
        between times ``ta`` and ``tb`` (in seconds). If ``tb`` is not
        provided, plays until the end of the clip, potentially forever.
        If ``tb`` is a negative value, ``tb`` is set to 
        `` clip.duration - tb. ``, for instance:
        
        >>> # cut the last two seconds of the clip:
        >>> newclip = clip.subclip(0,-2)
        
        If ``tb`` is provided or if the clip has a duration attribute,
        the duration of the returned clip is set automatically.
        The same effect is applied to the clip's audio and mask if any.
        """
        
        newclip = self.fl_time(lambda t: t + ta, applyto=[])
        if (tb is None) and (self.duration != None):
            tb = self.duration
        elif tb<0:
            if self.duration is None:
                print ("Error: subclip with negative times can only be"+
                        "be taken from clips with a ``duration``")
            else:
                tb = self.duration - tb
        if (tb != None):
            return newclip.set_duration(tb - ta)
        else:
            return newclip

    @apply_to_mask
    @apply_to_audio
    @time_can_be_tuple
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
