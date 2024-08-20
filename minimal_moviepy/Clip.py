"""
This module implements the central object of MoviePy, the Clip, and
all the methods that are common to the two subclasses of Clip, VideoClip
and AudioClip.
"""

from copy import copy

import numpy as np

from minimal_moviepy.decorators import (apply_to_audio, apply_to_mask,
                                convert_to_seconds, outplace,
                                requires_duration, use_clip_fps_by_default)


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
       composition at which the clip stops playing (in seconds).

     duration:
       Duration of the clip (in seconds). Some clips are infinite, in
       this case their duration will be ``None``.

     """
   
    # prefix for all temporary video and audio files.
    # You can overwrite it with 
    # >>> Clip._TEMP_FILES_PREFIX = "temp_"

    _TEMP_FILES_PREFIX = 'TEMP_MPY_'

    def __init__(self):

        self.start = 0
        self.end = None
        self.duration = None

        self.memoize = False
        self.memoized_t = None
        self.memoize_frame = None

    def copy(self):
        """ Shallow copy of the clip. 
        
        Returns a shallow copy of the clip whose mask and audio will
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
        elif self.end is not None:
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
        if self.end is None: return
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
            if self.duration is None:
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

            if (self.end is not None) and (tmin >= self.end):
                return False

            if tmax < self.start:
                return False

            # If we arrive here, a part of t falls in the clip
            result = 1 * (t >= self.start)
            if self.end is not None:
                result *= (t <= self.end)
            return result

        else:

            return((t >= self.start) and
                   ((self.end is None) or (t < self.end)))



    @requires_duration
    @use_clip_fps_by_default
    def iter_frames(self, fps=None, with_times = False,
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
        for t in np.arange(0, self.duration, 1.0/fps):
            frame = self.get_frame(t)
            if (dtype is not None) and (frame.dtype != dtype):
                frame = frame.astype(dtype)
            if with_times:
                yield t, frame
            else:
                yield frame

    def close(self):
        """ 
            Release any resources that are in use.
        """

        #    Implementation note for subclasses:
        #
        #    * Memory-based resources can be left to the garbage-collector.
        #    * However, any open files should be closed, and subprocesses
        #      should be terminated.
        #    * Be wary that shallow copies are frequently used.
        #      Closing a Clip may affect its copies.
        #    * Therefore, should NOT be called by __del__().
        pass

    # Support the Context Manager protocol, to ensure that resources are cleaned up.

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
