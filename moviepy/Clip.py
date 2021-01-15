"""
This module implements the central object of MoviePy, the Clip, and
all the methods that are common to the two subclasses of Clip, VideoClip
and AudioClip.
"""

from copy import copy

import numpy as np
import proglog

from moviepy.decorators import (
    apply_to_audio,
    apply_to_mask,
    convert_parameter_to_seconds,
    outplace,
    requires_duration,
    use_clip_fps_by_default,
)


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

    _TEMP_FILES_PREFIX = "TEMP_MPY_"

    def __init__(self):

        self.start = 0
        self.end = None
        self.duration = None

        self.memoize = False
        self.memoized_t = None
        self.memoized_frame = None

    def copy(self):
        """Shallow copy of the clip.

        Returns a shallow copy of the clip whose mask and audio will
        be shallow copies of the clip's mask and audio if they exist.

        This method is intensively used to produce new clips every time
        there is an outplace transformation of the clip (clip.resize,
        clip.subclip, etc.)
        """

        new_clip = copy(self)
        if hasattr(self, "audio"):
            new_clip.audio = copy(self.audio)
        if hasattr(self, "mask"):
            new_clip.mask = copy(self.mask)

        return new_clip

    @convert_parameter_to_seconds(["t"])
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
            # print(t)
            return self.make_frame(t)

    def transform(self, func, apply_to=None, keep_duration=True):
        """General processing of a clip.

        Returns a new Clip whose frames are a transformation
        (through function ``func``) of the frames of the current clip.

        Parameters
        -----------

        func
          A function with signature (gf,t -> frame) where ``gf`` will
          represent the current clip's ``get_frame`` method,
          i.e. ``gf`` is a function (t->image). Parameter `t` is a time
          in seconds, `frame` is a picture (=Numpy array) which will be
          returned by the transformed clip (see examples below).

        apply_to
          Can be either ``'mask'``, or ``'audio'``, or
          ``['mask','audio']``.
          Specifies if the filter should also be applied to the
          audio or the mask of the clip, if any.

        keep_duration
          Set to True if the transformation does not change the
          ``duration`` of the clip.

        Examples
        --------

        In the following ``new_clip`` a 100 pixels-high clip whose video
        content scrolls from the top to the bottom of the frames of
        ``clip`` at 50 pixels per second.

        >>> filter = lambda get_frame,t : get_frame(t)[int(t):int(t)+50, :]
        >>> new_clip = clip.transform(filter, apply_to='mask')

        """
        if apply_to is None:
            apply_to = []

        # mf = copy(self.make_frame)
        new_clip = self.with_make_frame(lambda t: func(self.get_frame, t))

        if not keep_duration:
            new_clip.duration = None
            new_clip.end = None

        if isinstance(apply_to, str):
            apply_to = [apply_to]

        for attribute in apply_to:
            attribute_value = getattr(new_clip, attribute, None)
            if attribute_value is not None:
                new_attribute_value = attribute_value.transform(
                    func, keep_duration=keep_duration
                )
                setattr(new_clip, attribute, new_attribute_value)

        return new_clip

    def time_transform(self, time_func, apply_to=None, keep_duration=False):
        """
        Returns a Clip instance playing the content of the current clip
        but with a modified timeline, time ``t`` being replaced by another
        time `time_func(t)`.

        Parameters
        -----------

        time_func:
          A function ``t -> new_t``

        apply_to:
          Can be either 'mask', or 'audio', or ['mask','audio'].
          Specifies if the filter ``transform`` should also be applied to the
          audio or the mask of the clip, if any.

        keep_duration:
          ``False`` (default) if the transformation modifies the
          ``duration`` of the clip.

        Examples
        --------

        >>> # plays the clip (and its mask and sound) twice faster
        >>> new_clip = clip.time_transform(lambda t: 2*t, apply_to=['mask', 'audio'])
        >>>
        >>> # plays the clip starting at t=3, and backwards:
        >>> new_clip = clip.time_transform(lambda t: 3-t)

        """
        if apply_to is None:
            apply_to = []

        return self.transform(
            lambda get_frame, t: get_frame(time_func(t)),
            apply_to,
            keep_duration=keep_duration,
        )

    def fx(self, func, *args, **kwargs):
        """

        Returns the result of ``func(self, *args, **kwargs)``.
        for instance

        >>> new_clip = clip.fx(resize, 0.2, method="bilinear")

        is equivalent to

        >>> new_clip = resize(clip, 0.2, method="bilinear")

        The motivation of fx is to keep the name of the effect near its
        parameters when the effects are chained:

        >>> from moviepy.video.fx import multiply_volume, resize, mirrorx
        >>> clip.fx(multiply_volume, 0.5).fx(resize, 0.3).fx(mirrorx)
        >>> # Is equivalent, but clearer than
        >>> mirrorx(resize(multiply_volume(clip, 0.5), 0.3))
        """

        return func(self, *args, **kwargs)

    @apply_to_mask
    @apply_to_audio
    @convert_parameter_to_seconds(["t"])
    @outplace
    def with_start(self, t, change_end=True):
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
    @convert_parameter_to_seconds(["t"])
    @outplace
    def with_end(self, t):
        """
        Returns a copy of the clip, with the ``end`` attribute set to
        ``t``, which can be expressed in seconds (15.35), in (min, sec),
        in (hour, min, sec), or as a string: '01:03:05.35'.
        Also sets the duration of the mask and audio, if any,
        of the returned clip.
        """
        self.end = t
        if self.end is None:
            return
        if self.start is None:
            if self.duration is not None:
                self.start = max(0, t - self.duration)
        else:
            self.duration = self.end - self.start

    @apply_to_mask
    @apply_to_audio
    @convert_parameter_to_seconds(["t"])
    @outplace
    def with_duration(self, duration, change_end=True):
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
        self.duration = duration

        if change_end:
            self.end = None if (duration is None) else (self.start + duration)
        else:
            if self.duration is None:
                raise Exception("Cannot change clip start when new duration is None")
            self.start = self.end - duration

    @outplace
    def with_make_frame(self, make_frame):
        """
        Sets a ``make_frame`` attribute for the clip. Useful for setting
        arbitrary/complicated videoclips.
        """
        self.make_frame = make_frame

    def with_fps(self, fps, change_duration=False):
        """Returns a copy of the clip with a new default fps for functions like
        write_videofile, iterframe, etc.
        If ``change_duration=True``, then the video speed will change to match the
        new fps (conserving all frames 1:1). For example, if the fps is
        halved in this mode, the duration will be doubled."""

        if change_duration:
            from moviepy.video.fx.speedx import speedx

            newclip = speedx(self, fps / self.fps)
        else:
            newclip = self.copy()

        newclip.fps = fps
        return newclip

    @outplace
    def with_is_mask(self, is_mask):
        """ Says wheter the clip is a mask or not (is_mask is a boolean)"""
        self.is_mask = is_mask

    @outplace
    def with_memoize(self, memoize):
        """ Sets wheter the clip should keep the last frame read in memory """
        self.memoize = memoize

    @convert_parameter_to_seconds(["t"])
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
                result *= t <= self.end
            return result

        else:

            return (t >= self.start) and ((self.end is None) or (t < self.end))

    @convert_parameter_to_seconds(["start_time", "end_time"])
    @apply_to_mask
    @apply_to_audio
    def subclip(self, start_time=0, end_time=None):
        """
        Returns a clip playing the content of the current clip
        between times ``start_time`` and ``end_time``, which can be expressed
        in seconds (15.35), in (min, sec), in (hour, min, sec), or as a
        string: '01:03:05.35'.
        If ``end_time`` is not provided, it is assumed to be the duration
        of the clip (potentially infinite).
        If ``end_time`` is a negative value, it is reset to
        ``clip.duration + end_time. ``. For instance: ::

            >>> # cut the last two seconds of the clip:
            >>> new_clip = clip.subclip(0,-2)

        If ``end_time`` is provided or if the clip has a duration attribute,
        the duration of the returned clip is set automatically.

        The ``mask`` and ``audio`` of the resulting subclip will be
        subclips of ``mask`` and ``audio`` the original clip, if
        they exist.
        """

        if start_time < 0:
            # Make this more Python-like, a negative value means to move
            # backward from the end of the clip
            start_time = self.duration + start_time  # Remember start_time is negative

        if (self.duration is not None) and (start_time > self.duration):
            raise ValueError(
                "start_time (%.02f) " % start_time
                + "should be smaller than the clip's "
                + "duration (%.02f)." % self.duration
            )

        new_clip = self.time_transform(lambda t: t + start_time, apply_to=[])

        if (end_time is None) and (self.duration is not None):

            end_time = self.duration

        elif (end_time is not None) and (end_time < 0):

            if self.duration is None:

                print(
                    "Error: subclip with negative times (here %s)"
                    % (str((start_time, end_time)))
                    + " can only be extracted from clips with a ``duration``"
                )

            else:

                end_time = self.duration + end_time

        if end_time is not None:

            new_clip.duration = end_time - start_time
            new_clip.end = new_clip.start + new_clip.duration

        return new_clip

    @apply_to_mask
    @apply_to_audio
    @convert_parameter_to_seconds(["start_time", "end_time"])
    def cutout(self, start_time, end_time):
        """
        Returns a clip playing the content of the current clip but
        skips the extract between ``start_time`` and ``end_time``, which can be
        expressed in seconds (15.35), in (min, sec), in (hour, min, sec),
        or as a string: '01:03:05.35'.
        If the original clip has a ``duration`` attribute set,
        the duration of the returned clip  is automatically computed as
        `` duration - (end_time - start_time)``.

        The resulting clip's ``audio`` and ``mask`` will also be cutout
        if they exist.
        """

        new_clip = self.time_transform(
            lambda t: t + (t >= start_time) * (end_time - start_time)
        )

        if self.duration is not None:

            return new_clip.with_duration(self.duration - (end_time - start_time))

        else:

            return new_clip

    @requires_duration
    @use_clip_fps_by_default
    def iter_frames(self, fps=None, with_times=False, logger=None, dtype=None):
        """Iterates over all the frames of the clip.

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
        >>> from moviepy import VideoFileClip
        >>> myclip = VideoFileClip('myvideo.mp4')
        >>> print ( [frame[0,:,0].max()
                     for frame in myclip.iter_frames()])
        """
        logger = proglog.default_bar_logger(logger)
        for frame_index in logger.iter_bar(t=np.arange(0, int(self.duration * fps))):
            # int is used to ensure that floating point errors are rounded
            # down to the nearest integer
            t = frame_index / fps

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

    def __eq__(self, other):
        if not isinstance(other, Clip):
            return NotImplemented

        # Make sure that the total number of frames is the same
        self_length = self.duration * self.fps
        other_length = other.duration * other.fps
        if self_length != other_length:
            return False

        # Make sure that each frame is the same
        for frame1, frame2 in zip(self.iter_frames(), other.iter_frames()):
            if not np.array_equal(frame1, frame2):
                return False

        return True

    # Support the Context Manager protocol, to ensure that resources are cleaned up.

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
