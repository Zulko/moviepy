"""Implements the central object of MoviePy, the Clip, and all the methods that
are common to the two subclasses of Clip, VideoClip and AudioClip.
"""

import copy as _copy
from functools import reduce
from numbers import Real
from operator import add
from typing import TYPE_CHECKING, List

import numpy as np
import proglog


if TYPE_CHECKING:
    from moviepy.Effect import Effect

from moviepy.decorators import (
    apply_to_audio,
    apply_to_mask,
    convert_parameter_to_seconds,
    outplace,
    requires_duration,
    use_clip_fps_by_default,
)


class Clip:
    """Base class of all clips (VideoClips and AudioClips).

    Attributes
    ----------

    start : float
      When the clip is included in a composition, time of the
      composition at which the clip starts playing (in seconds).

    end : float
      When the clip is included in a composition, time of the
      composition at which the clip stops playing (in seconds).

    duration : float
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
        """Allows the usage of ``.copy()`` in clips as chained methods invocation."""
        return _copy.copy(self)

    @convert_parameter_to_seconds(["t"])
    def get_frame(self, t) -> np.ndarray:
        """Gets a numpy array representing the RGB picture of the clip,
        or (mono or stereo) value for a sound clip, at time ``t``.

        Parameters
        ----------

        t : float or tuple or str
          Moment of the clip whose frame will be returned.


        """
        # Coming soon: smart error handling for debugging at this point
        if self.memoize:
            if t == self.memoized_t:
                return self.memoized_frame
            else:
                frame = self.frame_function(t)
                self.memoized_t = t
                self.memoized_frame = frame
                return frame
        else:
            return self.frame_function(t)

    def transform(self, func, apply_to=None, keep_duration=True):
        """General processing of a clip.

        Returns a new Clip whose frames are a transformation
        (through function ``func``) of the frames of the current clip.

        Parameters
        ----------

        func : function
          A function with signature (gf,t -> frame) where ``gf`` will
          represent the current clip's ``get_frame`` method,
          i.e. ``gf`` is a function (t->image). Parameter `t` is a time
          in seconds, `frame` is a picture (=Numpy array) which will be
          returned by the transformed clip (see examples below).

        apply_to : {"mask", "audio", ["mask", "audio"]}, optional
          Can be either ``'mask'``, or ``'audio'``, or
          ``['mask','audio']``.
          Specifies if the filter should also be applied to the
          audio or the mask of the clip, if any.

        keep_duration : bool, optional
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

        # mf = copy(self.frame_function)
        new_clip = self.with_updated_frame_function(lambda t: func(self.get_frame, t))

        # Internal ffmpeg fast-path metadata is only valid for raw reader clips.
        # Any transform/effect makes it unsafe.
        for _attr in (
            "_ffmpeg_source_filename",
            "_ffmpeg_source_start",
            "_ffmpeg_source_target_resolution",
            "_ffmpeg_source_resize_algorithm",
        ):
            try:
                if hasattr(new_clip, _attr):
                    delattr(new_clip, _attr)
            except Exception:
                pass

        # Batch GPU decode hooks are only safe for raw reader clips.
        # Any transform makes them unsafe (it would bypass the transform).
        try:
            if hasattr(new_clip, "_gpu_frame_function_batch_by_index"):
                delattr(new_clip, "_gpu_frame_function_batch_by_index")
            new_clip._gpu_batch_safe = False
        except Exception:
            pass

        # Best-effort internal GPU frame-function propagation.
        #
        # If the experimental GPU render path is enabled, it can use this to keep
        # effect chains on the GPU when their operations are CuPy-aware.
        #
        # This never changes public APIs and is only used opportunistically.
        try:
            def _gpu_frame_function(t):
                from moviepy.video.tools import cupy_utils

                cp = cupy_utils.cupy()

                def _is_gpu_frame_object(x):
                    # Support non-array GPU frame carriers (e.g. NV12 wrappers)
                    # by recognizing the protocol PyNvVideoCodec expects.
                    return callable(getattr(x, "cuda", None))

                def _gf(tt):
                    src_gpu_fn = getattr(self, "_gpu_frame_function", None)
                    if src_gpu_fn is not None:
                        try:
                            v = src_gpu_fn(tt)
                            if cupy_utils.is_cuda_array(v) or _is_gpu_frame_object(v):
                                return v
                            # Allow passing plane tuples/lists through.
                            if isinstance(v, (tuple, list)) and v and all(
                                cupy_utils.is_cuda_array(p) for p in v
                            ):
                                return v
                            return cp.asarray(v)
                        except Exception:
                            pass

                    v = self.get_frame(tt)
                    if cupy_utils.is_cuda_array(v) or _is_gpu_frame_object(v):
                        return v
                    if isinstance(v, (tuple, list)) and v and all(
                        cupy_utils.is_cuda_array(p) for p in v
                    ):
                        return v
                    return cp.asarray(v)

                try:
                    out = func(_gf, t)
                except Exception:
                    # Fallback: compute on CPU, then upload.
                    out = func(self.get_frame, t)

                if cupy_utils.is_cuda_array(out) or _is_gpu_frame_object(out):
                    return out
                if isinstance(out, (tuple, list)) and out and all(
                    cupy_utils.is_cuda_array(p) for p in out
                ):
                    return out
                return cp.asarray(out)

            new_clip._gpu_frame_function = _gpu_frame_function
        except Exception:
            pass

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
        but with a modified timeline, time ``t`` being replaced by the return
        of `time_func(t)`.

        Parameters
        ----------

        time_func : function
          A function ``t -> new_t``.

        apply_to : {"mask", "audio", ["mask", "audio"]}, optional
          Can be either 'mask', or 'audio', or ['mask','audio'].
          Specifies if the filter ``transform`` should also be applied to the
          audio or the mask of the clip, if any.

        keep_duration : bool, optional
          ``False`` (default) if the transformation modifies the
          ``duration`` of the clip.

        Examples
        --------

        .. code:: python

            # plays the clip (and its mask and sound) twice faster
            new_clip = clip.time_transform(lambda t: 2*t, apply_to=['mask', 'audio'])

            # plays the clip starting at t=3, and backwards:
            new_clip = clip.time_transform(lambda t: 3-t)

        """
        if apply_to is None:
            apply_to = []

        return self.transform(
            lambda get_frame, t: get_frame(time_func(t)),
            apply_to,
            keep_duration=keep_duration,
        )

    def with_effects(self, effects: List["Effect"]):
        """Return a copy of the current clip with the effects applied

        >>> new_clip = clip.with_effects([vfx.Resize(0.2, method="bilinear")])

        You can also pass multiple effect as a list

        >>> clip.with_effects([afx.VolumeX(0.5), vfx.Resize(0.3), vfx.Mirrorx()])
        """
        new_clip = self.copy()
        for effect in effects:
            # We always copy effect before using it, see Effect.copy
            # to see why we need to
            effect_copy = effect.copy()
            new_clip = effect_copy.apply(new_clip)

        return new_clip

    @apply_to_mask
    @apply_to_audio
    @convert_parameter_to_seconds(["t"])
    @outplace
    def with_start(self, t, change_end=True):
        """Returns a copy of the clip, with the ``start`` attribute set
        to ``t``, which can be expressed in seconds (15.35), in (min, sec),
        in (hour, min, sec), or as a string: '01:03:05.35'.

        These changes are also applied to the ``audio`` and ``mask``
        clips of the current clip, if they exist.

        note::
          The start and end attribute of a clip define when a clip will start
          playing when used in a composite video clip, not the start time of
          the clip itself.

          i.e: with_start(10) mean the clip will still start at his first frame,
          but if used in a composite video clip it will only start to show at
          10 seconds.

        Parameters
        ----------

        t : float or tuple or str
          New ``start`` attribute value for the clip.

        change_end : bool optional
          Indicates if the ``end`` attribute value must be changed accordingly,
          if possible. If ``change_end=True`` and the clip has a ``duration``
          attribute, the ``end`` attribute of the clip will be updated to
          ``start + duration``. If ``change_end=False`` and the clip has a
          ``end`` attribute, the ``duration`` attribute of the clip will be
          updated to ``end - start``.
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
        """Returns a copy of the clip, with the ``end`` attribute set to ``t``,
        which can be expressed in seconds (15.35), in (min, sec), in
        (hour, min, sec), or as a string: '01:03:05.35'. Also sets the duration
        of the mask and audio, if any, of the returned clip.

        note::
          The start and end attribute of a clip define when a clip will start
          playing when used in a composite video clip, not the start time of
          the clip itself.

          i.e: with_start(10) mean the clip will still start at his first frame,
          but if used in a composite video clip it will only start to show at
          10 seconds.

        Parameters
        ----------

        t : float or tuple or str
          New ``end`` attribute value for the clip.
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
    @convert_parameter_to_seconds(["duration"])
    @outplace
    def with_duration(self, duration, change_end=True):
        """Returns a copy of the clip, with the  ``duration`` attribute set to
        ``t``, which can be expressed in seconds (15.35), in (min, sec), in
        (hour, min, sec), or as a string: '01:03:05.35'. Also sets the duration
        of the mask and audio, if any, of the returned clip.

        If ``change_end is False``, the start attribute of the clip will be
        modified in function of the duration and the preset end of the clip.

        Parameters
        ----------

        duration : float
          New duration attribute value for the clip.

        change_end : bool, optional
          If ``True``, the ``end`` attribute value of the clip will be adjusted
          accordingly to the new duration using ``clip.start + duration``.
        """
        self.duration = duration

        if change_end:
            self.end = None if (duration is None) else (self.start + duration)
        else:
            if self.duration is None:
                raise ValueError("Cannot change clip start when new duration is None")
            self.start = self.end - duration

    @outplace
    def with_updated_frame_function(self, frame_function):
        """Sets a ``frame_function`` attribute for the clip. Useful for setting
        arbitrary/complicated videoclips.

        Parameters
        ----------

        frame_function : function
          New frame creator function for the clip.
          A frame_function is a function taking a time ``t`` as input and
          returning a frame (a numpy array) as a result.
        """
        self.frame_function = frame_function

    def with_fps(self, fps, change_duration=False):
        """Returns a copy of the clip with a new default fps for functions like
        write_videofile, iterframe, etc.

        Parameters
        ----------

        fps : int
          New ``fps`` attribute value for the clip.

        change_duration : bool, optional
          If ``change_duration=True``, then the video speed will change to
          match the new fps (conserving all frames 1:1). For example, if the
          fps is halved in this mode, the duration will be doubled.
        """
        if change_duration:
            from moviepy.video.fx.MultiplySpeed import MultiplySpeed

            newclip = self.with_effects([MultiplySpeed(fps / self.fps)])
        else:
            newclip = self.copy()

        newclip.fps = fps
        return newclip

    @outplace
    def with_is_mask(self, is_mask):
        """Says whether the clip is a mask or not.

        Parameters
        ----------

        is_mask : bool
          New ``is_mask`` attribute value for the clip.
        """
        self.is_mask = is_mask

    @outplace
    def with_memoize(self, memoize):
        """Sets whether the clip should keep the last frame read in memory.

        Parameters
        ----------

        memoize : bool
          Indicates if the clip should keep the last frame read in memory.
        """
        self.memoize = memoize

    @convert_parameter_to_seconds(["start_time", "end_time"])
    @apply_to_mask
    @apply_to_audio
    def subclipped(self, start_time=0, end_time=None):
        """Returns a clip playing the content of the current clip between times
        ``start_time`` and ``end_time``, which can be expressed in seconds
        (15.35), in (min, sec), in (hour, min, sec), or as a string:
        '01:03:05.35'.

        The ``mask`` and ``audio`` of the resulting subclip will be subclips of
        ``mask`` and ``audio`` the original clip, if they exist.

        It's equivalent to slice the clip as a sequence, like
        ``clip[t_start:t_end]``.

        Parameters
        ----------

        start_time : float or tuple or str, optional
          Moment that will be chosen as the beginning of the produced clip. If
          is negative, it is reset to ``clip.duration + start_time``.

        end_time : float or tuple or str, optional
          Moment that will be chosen as the end of the produced clip. If not
          provided, it is assumed to be the duration of the clip (potentially
          infinite). If is negative, it is reset to ``clip.duration + end_time``.
          For instance:

          >>> # cut the last two seconds of the clip:
          >>> new_clip = clip.subclipped(0, -2)

          If ``end_time`` is provided or if the clip has a duration attribute,
          the duration of the returned clip is set automatically.
        """
        if start_time < 0:
            # Make this more Python-like, a negative value means to move
            # backward from the end of the clip
            start_time = self.duration + start_time  # Remember start_time is negative

        if (self.duration is not None) and (start_time >= self.duration):
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
                raise ValueError(
                    (
                        "Subclip with negative times (here %s)"
                        " can only be extracted from clips with a ``duration``"
                    )
                    % (str((start_time, end_time)))
                )

            else:
                end_time = self.duration + end_time

        if end_time is not None:
            # Allow a slight tolerance to account for rounding errors
            if (self.duration is not None) and (end_time - self.duration > 0.00000001):
                raise ValueError(
                    "end_time (%.02f) " % end_time
                    + "should be smaller or equal to the clip's "
                    + "duration (%.02f)." % self.duration
                )

            new_clip.duration = end_time - start_time
            new_clip.end = new_clip.start + new_clip.duration

        # Internal ffmpeg fast-path metadata propagation.
        # If this clip is a raw VideoFileClip (or already a raw subclip of one),
        # keep track of the source file and absolute trim window.
        try:
            src = getattr(self, "_ffmpeg_source_filename", None)
            src_start = getattr(self, "_ffmpeg_source_start", None)
            src_target_res = getattr(self, "_ffmpeg_source_target_resolution", None)
            src_resize_algo = getattr(self, "_ffmpeg_source_resize_algorithm", None)
            if src is not None and src_start is not None:
                new_clip._ffmpeg_source_filename = src
                new_clip._ffmpeg_source_target_resolution = src_target_res
                new_clip._ffmpeg_source_resize_algorithm = src_resize_algo
                new_clip._ffmpeg_source_start = float(src_start) + float(start_time)
        except Exception:
            pass

        return new_clip

    @convert_parameter_to_seconds(["start_time", "end_time"])
    def with_section_cut_out(self, start_time, end_time):
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

        Parameters
        ----------

        start_time : float or tuple or str
          Moment from which frames will be ignored in the resulting output.

        end_time : float or tuple or str
          Moment until which frames will be ignored in the resulting output.
        """
        new_clip = self.time_transform(
            lambda t: t + (t >= start_time) * (end_time - start_time),
            apply_to=["audio", "mask"],
        )

        if self.duration is not None:
            return new_clip.with_duration(self.duration - (end_time - start_time))
        else:  # pragma: no cover
            return new_clip

    def with_speed_scaled(self, factor: float = None, final_duration: float = None):
        """Returns a clip playing the current clip but at a speed multiplied
        by ``factor``. For info on the parameters, please see ``vfx.MultiplySpeed``.
        """
        from moviepy.video.fx.MultiplySpeed import MultiplySpeed

        return self.with_effects(
            [MultiplySpeed(factor=factor, final_duration=final_duration)]
        )

    def with_volume_scaled(self, factor: float, start_time=None, end_time=None):
        """Returns a new clip with audio volume multiplied by the value `factor`.
        For info on the parameters, please see ``afx.MultiplyVolume``
        """
        from moviepy.audio.fx.MultiplyVolume import MultiplyVolume

        return self.with_effects(
            [MultiplyVolume(factor=factor, start_time=start_time, end_time=end_time)]
        )

    @requires_duration
    @use_clip_fps_by_default
    def iter_frames(self, fps=None, with_times=False, logger=None, dtype=None):
        """Iterates over all the frames of the clip.

        Returns each frame of the clip as a HxWxN Numpy array,
        where N=1 for mask clips and N=3 for RGB clips.

        This function is not really meant for video editing. It provides an
        easy way to do frame-by-frame treatment of a video, for fields like
        science, computer vision...

        Parameters
        ----------

        fps : int, optional
          Frames per second for clip iteration. Is optional if the clip already
          has a ``fps`` attribute.

        with_times : bool, optional
          Ff ``True`` yield tuples of ``(t, frame)`` where ``t`` is the current
          time for the frame, otherwise only a ``frame`` object.

        logger : str, optional
          Either ``"bar"`` for progress bar or ``None`` or any Proglog logger.

        dtype : type, optional
          Type to cast Numpy array frames. Use ``dtype="uint8"`` when using the
          pictures to write video, images..

        Examples
        --------


        .. code:: python

            # prints the maximum of red that is contained
            # on the first line of each frame of the clip.
            from moviepy import VideoFileClip
            myclip = VideoFileClip('myvideo.mp4')
            print([frame[0,:,0].max()
                  for frame in myclip.iter_frames()])
        """
        logger = proglog.default_bar_logger(logger)

        # Normalize dtype to a numpy dtype to support common inputs like "uint8".
        # This also avoids triggering an unnecessary .astype() for every frame.
        target_dtype = None if dtype is None else np.dtype(dtype)

        # int() ensures floating point errors are rounded down.
        n_frames = int(self.duration * fps)

        for frame_index in logger.iter_bar(frame_index=range(n_frames)):
            # Use numpy float arithmetic for t to preserve historical behavior.
            # Some algorithms use exact float keys (e.g. in moviepy.video.tools.cuts),
            # so we avoid small rounding differences from precomputed reciprocals.
            t = np.float64(frame_index) / fps

            frame = self.get_frame(t)

            # Public API: iter_frames yields NumPy arrays. If a clip returns
            # a CuPy/CUDA array internally, download it best-effort here.
            if hasattr(frame, "__cuda_array_interface__"):
                try:
                    import cupy as cp

                    frame = cp.asnumpy(frame)
                except Exception:
                    pass
            if (target_dtype is not None) and (frame.dtype != target_dtype):
                frame = frame.astype(target_dtype)

            if with_times:
                yield t, frame
            else:
                yield frame

    @requires_duration
    @use_clip_fps_by_default
    def iter_frames_gpu(self, fps=None, with_times=False, logger=None, dtype=None):
        """Iterate over frames, yielding GPU arrays (CuPy) when possible.

        This is a best-effort internal helper intended for GPU-accelerated export
        and custom pipelines. If CuPy is unavailable, it yields NumPy frames.

        Unlike `iter_frames`, this method does not force frames onto the CPU.
        """
        logger = proglog.default_bar_logger(logger)
        target_dtype = None if dtype is None else np.dtype(dtype)
        n_frames = int(self.duration * fps)

        cp = None
        try:
            from moviepy.video.tools import cupy_utils

            cp = cupy_utils.cupy()
        except Exception:
            cp = None

        gpu_fn = getattr(self, "_gpu_frame_function", None)

        for frame_index in logger.iter_bar(frame_index=range(n_frames)):
            t = np.float64(frame_index) / fps
            frame = None

            if cp is None:
                frame = self.get_frame(t)
            else:
                try:
                    frame = gpu_fn(t) if gpu_fn is not None else self.get_frame(t)
                    if not hasattr(frame, "__cuda_array_interface__"):
                        frame = cp.asarray(frame)
                except Exception:
                    frame = self.get_frame(t)
                    if not hasattr(frame, "__cuda_array_interface__"):
                        frame = cp.asarray(frame)

            if (
                (target_dtype is not None)
                and hasattr(frame, "dtype")
                and (frame.dtype != target_dtype)
            ):
                try:
                    frame = frame.astype(target_dtype)
                except Exception:
                    pass

            if with_times:
                yield t, frame
            else:
                yield frame

    @convert_parameter_to_seconds(["t"])
    def is_playing(self, t):
        """If ``t`` is a time, returns true if t is between the start and the end
        of the clip. ``t`` can be expressed in seconds (15.35), in (min, sec), in
        (hour, min, sec), or as a string: '01:03:05.35'. If ``t`` is a numpy
        array, returns False if none of the ``t`` is in the clip, else returns a
        vector [b_1, b_2, b_3...] where b_i is true if tti is in the clip.
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

    def close(self):
        """Release any resources that are in use."""
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

    def __enter__(self):
        """
        Support the Context Manager protocol,
        to ensure that resources are cleaned up.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __getitem__(self, key):
        """
        Support extended slice and index operations over
        a clip object.

        Simple slicing is implemented via `subclip`.
        So, ``clip[t_start:t_end]`` is equivalent to
        ``clip.subclipped(t_start, t_end)``. If ``t_start`` is not
        given, default to ``0``, if ``t_end`` is not given,
        default to ``self.duration``.

        The slice object optionally support a third argument as
        a ``speed`` coefficient (that could be negative),
        ``clip[t_start:t_end:speed]``.

        For example ``clip[::-1]`` returns a reversed (a time_mirror fx)
        the video and ``clip[:5:2]`` returns the segment from 0 to 5s
        accelerated to 2x (ie. resulted duration would be 2.5s)

        In addition, a tuple of slices is supported, resulting in the concatenation
        of each segment. For example ``clip[(:1, 2:)]`` return a clip
        with the segment from 1 to 2s removed.

        If ``key`` is not a slice or tuple, we assume it's a time
        value (expressed in any format supported by `cvsec`)
        and return the frame at that time, passing the key
        to ``get_frame``.
        """
        apply_to = ["mask", "audio"]
        if isinstance(key, slice):
            # support for [start:end:speed] slicing. If speed is negative
            # a time mirror is applied.
            clip = self.subclipped(key.start or 0, key.stop or self.duration)

            if key.step:
                # change speed of the subclip
                factor = abs(key.step)
                if factor != 1:
                    # change speed
                    clip = clip.time_transform(
                        lambda t: factor * t, apply_to=apply_to, keep_duration=True
                    )
                    clip = clip.with_duration(1.0 * clip.duration / factor)
                if key.step < 0:
                    # time mirror
                    clip = clip.time_transform(
                        lambda t: clip.duration - t - 1 / self.fps,
                        keep_duration=True,
                        apply_to=apply_to,
                    )
            return clip
        elif isinstance(key, tuple):
            # get a concatenation of subclips
            return reduce(add, (self[k] for k in key))
        else:
            return self.get_frame(key)

    def __del__(self):
        # WARNING: as stated in close() above, if we call close, it closes clips
        # even if shallow copies are still in used, leading to some bugs, see:
        # https://github.com/Zulko/moviepy/issues/1994
        # so don't call self.close() here, rather do it manually in the code.
        pass

    def __add__(self, other):
        # concatenate. implemented in specialized classes
        return NotImplemented

    def __mul__(self, n):
        # loop n times where N is a real
        if not isinstance(n, Real):
            return NotImplemented

        from moviepy.video.fx.Loop import Loop

        return self.with_effects([Loop(n)])
