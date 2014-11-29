"""
This module implements the central object of MoviePy, the Clip, and
all the methods that are common to the two subclasses of Clip, VideoClip
and AudioClip.
"""

from copy import copy
import numpy as np

from moviepy.decorators import ( apply_to_mask,
                                 apply_to_audio,
                                 requires_duration,
                                 outplace,
                                 convert_to_seconds,
                                 use_clip_fps_by_default)
from tqdm import tqdm

class Clip:

    """
        
     Base class of all clips (VideoClips and AudioClips).
      
       
     Attributes
     -----------
     
     start:
       When the clip is included in a composition, time of the
       composition at which the clip starts playing (in seconds). 
     
     end:
       When the clip is included in a composition, time of the
       composition at which the clip starts playing (in seconds).
     
     duration:
       Duration of the clip (in seconds). Some clips are infinite, in
       this case their duration will be ``None``.
     
     """
    
    # prefix for all tmeporary video and audio files.
    # You can overwrite it with 
    # >>> Clip._TEMP_FILES_PREFIX = "temp_"
    
    _TEMP_FILES_PREFIX = 'TEMP_MPY_'

    def __init__(self):

        self.start = 0
        self.end = None
        self.duration = None
        
        self.memoize = False
        self.memoized_t = None
        self.memoize_frame  = None



    def copy(self):
        """ Shallow copy of the clip. 
        
        Returns a shwallow copy of the clip whose mask and audio will
        be shallow copies of the clip's mask and audio if they exist.
        
        This method is intensively used to produce new clips every time
        there is an outplace transformation of the clip (clip.resize,
        clip.subclip, etc.)
        """
        
        newclip = copy(self)
        if hasattr(self, 'audio'):
            newclip.audio = copy(self.audio)
        if hasattr(self, 'mask'):
            newclip.mask = copy(self.mask)
            
        return newclip
    
    @convert_to_seconds(['t'])
    def get_frame(self, t):
        """
        Gets a numpy array representing the RGB picture of the clip at time t
        or (mono or stereo) value for a sound clip
        """
        # Coming soon: smart error handling for debugging at this point 
        if self.memoize:
            if t == self.memoized_t:
                return self.memoized_frame
            else:
                frame = self.make_frame(t)
                self.memoized_t = t
                self.memoized_frame = frame
                return frame
        else:
            return self.make_frame(t)

    def fl(self, fun, apply_to=[] , keep_duration=True):
        """ General processing of a clip.

        Returns a new Clip whose frames are a transformation
        (through function ``fun``) of the frames of the current clip.
        
        Parameters
        -----------
        
        fun
          A function with signature (gf,t -> frame) where ``gf`` will
          represent the current clip's ``get_frame`` method,
          i.e. ``gf`` is a function (t->image). Parameter `t` is a time
          in seconds, `frame` is a picture (=Numpy array) which will be
          returned by the transformed clip (see examples below).
           
        apply_to
          Can be either ``'mask'``, or ``'audio'``, or
          ``['mask','audio']``.
          Specifies if the filter ``fl`` should also be applied to the
          audio or the mask of the clip, if any.
        
        keep_duration
          Set to True if the transformation does not change the
          ``duration`` of the clip.
          
        Examples
        --------
        
        In the following ``newclip`` a 100 pixels-high clip whose video
        content scrolls from the top to the bottom of the frames of
        ``clip``.
        
        >>> fl = lambda gf,t : gf(t)[int(t):int(t)+50, :]
        >>> newclip = clip.fl(fl, apply_to='mask')
        
        """

        #mf = copy(self.make_frame)
        newclip = self.set_make_frame(lambda t: fun(self.get_frame, t))
        
        if not keep_duration:
            newclip.duration = None
            newclip.end = None
            
        if isinstance(apply_to, str):
            apply_to = [apply_to]

        for attr in apply_to:
            if hasattr(newclip, attr):
                a = getattr(newclip, attr)
                if a is not None:
                    new_a =  a.fl(fun, keep_duration=keep_duration)
                    setattr(newclip, attr, new_a)
                    
        return newclip

    
    
    def fl_time(self, t_func, apply_to=[], keep_duration=False):
        """
        Returns a Clip instance playing the content of the current clip
        but with a modified timeline, time ``t`` being replaced by another
        time `t_func(t)`.
        
        Parameters
        -----------
        
        t_func:
          A function ``t-> new_t``
        
        apply_to:
          Can be either 'mask', or 'audio', or ['mask','audio'].
          Specifies if the filter ``fl`` should also be applied to the
          audio or the mask of the clip, if any.
        
        keep_duration:
          ``False`` (default) if the transformation modifies the
          ``duration`` of the clip.
          
        Examples
        --------
        
        >>> # plays the clip (and its mask and sound) twice faster
        >>> newclip = clip.fl_time(lambda: 2*t, apply_to=['mask','audio'])
        >>>
        >>> # plays the clip starting at t=3, and backwards:
        >>> newclip = clip.fl_time(lambda: 3-t)
        
        """
        
        return self.fl(lambda gf, t: gf(t_func(t)), apply_to,
                                    keep_duration=keep_duration)
    
    
    
    def fx(self, func, *args, **kwargs):
        """
        
        Returns the result of ``func(self, *args, **kwargs)``.
        for instance
        
        >>> newclip = clip.fx(resize, 0.2, method='bilinear')
        
        is equivalent to
        
        >>> newclip = resize(clip, 0.2, method='bilinear')
        
        The motivation of fx is to keep the name of the effect near its
        parameters, when the effects are chained:
        
        >>> from moviepy.video.fx import volumex, resize, mirrorx
        >>> clip.fx( volumex, 0.5).fx( resize, 0.3).fx( mirrorx )
        >>> # Is equivalent, but clearer than
        >>> resize( volumex( mirrorx( clip ), 0.5), 0.3)
        
        """
        
        return func(self, *args, **kwargs)
            
    
    
    @apply_to_mask
    @apply_to_audio
    @convert_to_seconds(['t'])
    @outplace
    def set_start(self, t, change_end=True):
        """
        Returns a copy of the clip, with the ``start`` attribute set
        to ``t``, which can be expressed in seconds (15.35), in (min, sec),
        in (hour, min, sec), or as a string: '01:03:05.35'.

        
        If ``change_end=True`` and the clip has a ``duration`` attribute,
        the ``end`` atrribute of the clip will be updated to
        ``start+duration``.
        
        If ``change_end=False`` and the clip has a ``end`` attribute,
        the ``duration`` attribute of the clip will be updated to 
        ``end-start``
        
        These changes are also applied to the ``audio`` and ``mask``
        clips of the current clip, if they exist.
        """
        
        self.start = t
        if (self.duration is not None) and change_end:
            self.end = t + self.duration
        elif (self.end is not None):
            self.duration = self.end - self.start
    
    
    
    @apply_to_mask
    @apply_to_audio
    @convert_to_seconds(['t'])
    @outplace
    def set_end(self, t):
        """
        Returns a copy of the clip, with the ``end`` attribute set to
        ``t``, which can be expressed in seconds (15.35), in (min, sec),
        in (hour, min, sec), or as a string: '01:03:05.35'.
        Also sets the duration of the mask and audio, if any,
        of the returned clip.
        """
        self.end = t
        if self.start is None:
            if self.duration is not None:
                self.start = max(0, t - newclip.duration)
        else:
            self.duration = self.end - self.start


    
    @apply_to_mask
    @apply_to_audio
    @convert_to_seconds(['t'])
    @outplace
    def set_duration(self, t, change_end=True):
        """
        Returns a copy of the clip, with the  ``duration`` attribute
        set to ``t``, which can be expressed in seconds (15.35), in (min, sec),
        in (hour, min, sec), or as a string: '01:03:05.35'.
        Also sets the duration of the mask and audio, if any, of the
        returned clip.
        If change_end is False, the start attribute of the clip will
        be modified in function of the duration and the preset end
        of the clip.
        """
        self.duration = t
        if change_end:
            self.end = None if (t is None) else (self.start + t)
        else:
            if duration is None:
                raise Exception("Cannot change clip start when new"
                                 "duration is None")
            self.start = self.end - t


    @outplace
    def set_make_frame(self, make_frame):
        """
        Sets a ``make_frame`` attribute for the clip. Useful for setting
        arbitrary/complicated videoclips.
        """
        self.make_frame = make_frame

    @outplace
    def set_fps(self, fps):
        """ Returns a copy of the clip with a new default fps for functions like
        write_videofile, iterframe, etc. """ 
        self.fps = fps


    @outplace
    def set_ismask(self, ismask):
        """ Says wheter the clip is a mask or not (ismask is a boolean)""" 
        self.ismask = ismask

    @outplace
    def set_memoize(self, memoize):
        """ Sets wheter the clip should keep the last frame read in memory """ 
        self.memoize = memoize    
    
    @convert_to_seconds(['t'])
    def is_playing(self, t):
        """
        
        If t is a time, returns true if t is between the start and
        the end of the clip. t can be expressed in seconds (15.35),
        in (min, sec), in (hour, min, sec), or as a string: '01:03:05.35'.
        If t is a numpy array, returns False if none of the t is in
        theclip, else returns a vector [b_1, b_2, b_3...] where b_i
        is true iff tti is in the clip. 
        """
        
        if isinstance(t, np.ndarray):
            # is the whole list of t outside the clip ?
            tmin, tmax = t.min(), t.max()
            
            if (self.end is not None) and (tmin >= self.end) :
                return False
            
            if tmax < self.start:
                return False
            
            # If we arrive here, a part of t falls in the clip
            result = 1 * (t >= self.start)
            if (self.end is not None):
                result *= (t <= self.end)
            return result
        
        else:
            
            return( (t >= self.start) and
                    ((self.end is None) or (t < self.end) ) )
    


    @convert_to_seconds(['t_start', 't_end'])
    @apply_to_mask
    @apply_to_audio
    def subclip(self, t_start=0, t_end=None):
        """
        Returns a clip playing the content of the current clip
        between times ``t_start`` and ``t_end``, which can be expressed
        in seconds (15.35), in (min, sec), in (hour, min, sec), or as a
        string: '01:03:05.35'.
        If ``t_end`` is not provided, it is assumed to be the duration
        of the clip (potentially infinite).
        If ``t_end`` is a negative value, it is reset to
        ``clip.duration + t_end. ``. For instance: ::
        
            >>> # cut the last two seconds of the clip:
            >>> newclip = clip.subclip(0,-2)
        
        If ``t_end`` is provided or if the clip has a duration attribute,
        the duration of the returned clip is set automatically.
        
        The ``mask`` and ``audio`` of the resulting subclip will be
        subclips of ``mask`` and ``audio`` the original clip, if
        they exist.
        """

        if (self.duration is not None) and (t_start>self.duration):
        
            raise ValueError("t_start (%.02f) "%t_start +
                             "should be smaller than the clip's "+
                             "duration (%.02f)."%self.duration)

        newclip = self.fl_time(lambda t: t + t_start, apply_to=[])
        
        if (t_end is None) and (self.duration is not None):
        
            t_end = self.duration
        
        elif t_end<0:
        
            if self.duration is None:
        
                print ("Error: subclip with negative times can only be"+
                        "extracted from clips with a ``duration``")
        
            else:
        
                t_end = self.duration + t_end
        
        if (t_end is not None):
        
            newclip.duration = t_end - t_start
            newclip.end = newclip.start + newclip.duration
            
        return newclip

    
    @apply_to_mask
    @apply_to_audio
    @convert_to_seconds(['ta', 'tb'])
    def cutout(self, ta, tb):
        """
        Returns a clip playing the content of the current clip but
        skips the extract between ``ta`` and ``tb``, which can be
        expressed in seconds (15.35), in (min, sec), in (hour, min, sec),
        or as a string: '01:03:05.35'.
        If the original clip has a ``duration`` attribute set,
        the duration of the returned clip  is automatically computed as
        `` duration - (tb - ta)``.
        
        The resulting clip's ``audio`` and ``mask`` will also be cutout
        if they exist.
        """
        
        fl = lambda t: t + (t >= ta)*(tb - ta)
        newclip = self.fl_time(fl)
        
        if self.duration is not None:
        
            return newclip.set_duration(self.duration - (tb - ta))
        
        else:
        
            return newclip

    @requires_duration
    @use_clip_fps_by_default
    def iter_frames(self, fps=None, with_times = False, progress_bar=False,
                    dtype=None):
        """ Iterates over all the frames of the clip.
        
        Returns each frame of the clip as a HxWxN np.array,
        where N=1 for mask clips and N=3 for RGB clips.
        
        This function is not really meant for video editing.
        It provides an easy way to do frame-by-frame treatment of
        a video, for fields like science, computer vision...
        
        The ``fps`` (frames per second) parameter is optional if the
        clip already has a ``fps`` attribute.

        Use dtype="uint8" when using the pictures to write video, images... 
        
        Examples
        ---------
        
        >>> # prints the maximum of red that is contained
        >>> # on the first line of each frame of the clip.
        >>> from moviepy.editor import VideoFileClip
        >>> myclip = VideoFileClip('myvideo.mp4')
        >>> print ( [frame[0,:,0].max()
                     for frame in myclip.iter_frames()])
        """

        def generator():
        
            for t in np.arange(0, self.duration, 1.0/fps):
        
                frame = self.get_frame(t)
        
                if (dtype is not None) and (frame.dtype != dtype):
        
                    frame = frame.astype(dtype)

                if with_times:
        
                    yield t, frame
        
                else:
        
                    yield frame
        
        if progress_bar:
        
            nframes = int(self.duration*fps)+1
            return tqdm(generator(), total=nframes)

        return generator()
