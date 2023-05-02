"""Decorators used by moviepy."""

from __future__ import annotations

import inspect
import os
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING

import decorator

from moviepy.tools import convert_to_seconds

if TYPE_CHECKING:
    from moviepy.Clip import Clip
    from moviepy.video.VideoClip import VideoClip
    from moviepy.types import ClipFunc, P, T, VideoClipFunc


@decorator.decorator
def outplace(func: ClipFunc[P], clip: Clip, *args: P.args, **kwargs: P.kwargs) -> Clip:
    """Applies ``func(clip.copy(), *args, **kwargs)`` and returns ``clip.copy()``."""
    newClip = clip.copy()
    func(newClip, *args, **kwargs)
    return newClip


@decorator.decorator
def convert_masks_to_RGB(
    func: VideoClipFunc[P], clip: VideoClip, *args: P.args, **kwargs: P.kwargs
) -> VideoClip:
    """If the clip is a mask, convert it to RGB before running the function."""
    if clip.is_mask:
        clip = clip.to_RGB()
    return func(clip, *args, **kwargs)


@decorator.decorator
def apply_to_mask(
    func: ClipFunc[P], clip: Clip, *args: P.args, **kwargs: P.kwargs
) -> Clip:
    """Applies the same function ``func`` to the mask of the clip created with
    ``func``.
    """
    newClip = func(clip, *args, **kwargs)
    if getattr(newClip, "mask", None):
        newClip.mask = func(newClip.mask, *args, **kwargs)
    return newClip


@decorator.decorator
def apply_to_audio(
    func: ClipFunc[P], clip: Clip, *args: P.args, **kwargs: P.kwargs
) -> Clip:
    """Applies the function ``func`` to the audio of the clip created with ``func``."""
    newClip = func(clip, *args, **kwargs)
    if getattr(newClip, "audio", None):
        newClip.audio = func(newClip.audio, *args, **kwargs)
    return newClip


@decorator.decorator
def requires_duration(
    func: ClipFunc[P], clip: Clip, *args: P.args, **kwargs: P.kwargs
) -> Clip:
    """Raises an error if the clip has no duration."""
    if clip.duration is None:
        raise ValueError("Attribute 'duration' not set")
    else:
        return func(clip, *args, **kwargs)


@decorator.decorator
def requires_fps(
    func: VideoClipFunc[P], clip: VideoClip, *args: P.args, **kwargs: P.kwargs
) -> VideoClip:
    """Raises an error if the clip has no fps."""
    if not hasattr(clip, "fps") or clip.fps is None:
        raise ValueError("Attribute 'fps' not set")
    else:
        return func(clip, *args, **kwargs)


@decorator.decorator
def audio_video_fx(
    func: ClipFunc[P], clip: Clip, *args: P.args, **kwargs: P.kwargs
) -> Clip:
    """Use an audio function on a video/audio clip.

    This decorator tells that the function func (audioclip -> audioclip)
    can be also used on a video clip, at which case it returns a
    videoclip with unmodified video and modified audio.
    """
    if hasattr(clip, "audio"):
        newClip = clip.copy()
        if clip.audio is not None:
            newClip.audio = func(clip.audio, *args, **kwargs)
        return newClip
    else:
        return func(clip, *args, **kwargs)


def preprocess_args(
    fun: Callable[P, T], varnames: Sequence[str]
) -> Callable[[Callable[P, T]], T]:
    """Applies fun to variables in varnames before launching the function."""

    def wrapper(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        names = inspect.getfullargspec(func).args
        new_args = [
            fun(arg) if (name in varnames) and (arg is not None) else arg
            for (arg, name) in zip(args, names)
        ]
        new_kwargs = {
            kwarg: fun(value) if kwarg in varnames else value
            for (kwarg, value) in kwargs.items()
        }
        return func(*new_args, **new_kwargs)

    return decorator.decorator(wrapper)


def convert_parameter_to_seconds(varnames: Sequence[str]):
    """Converts the specified variables to seconds."""
    return preprocess_args(convert_to_seconds, varnames)


def convert_path_to_string(varnames: Sequence[str]):
    """Converts the specified variables to a path string."""
    return preprocess_args(os.fspath, varnames)


@decorator.decorator
def add_mask_if_none(
    func: VideoClipFunc[P], clip: VideoClip, *args: P.args, **kwargs: P.kwargs
) -> VideoClip:
    """Add a mask to the clip if there is none."""
    if clip.mask is None:
        clip = clip.add_mask()
    return func(clip, *args, **kwargs)


@decorator.decorator
def useClip_fps_by_default(
    func: ClipFunc[P], clip: Clip, *args: P.args, **kwargs: P.kwargs
) -> Clip:
    """Will use ``clip.fps`` if no ``fps=...`` is provided in **kwargs**."""

    def find_fps(fps: int | None) -> int:
        if fps is not None:
            return fps
        elif getattr(clip, "fps", None):
            return clip.fps
        raise AttributeError(
            "No 'fps' (frames per second) attribute specified"
            " for function %s and the clip has no 'fps' attribute. Either"
            " provide e.g. fps=24 in the arguments of the function, or define"
            " the clip's fps with `clip.fps=24`" % func.__name__
        )

    names = inspect.getfullargspec(func).args[1:]

    new_args = [
        find_fps(arg) if (name == "fps") else arg for (arg, name) in zip(args, names)
    ]
    new_kwargs = {
        kwarg: find_fps(value) if kwarg == "fps" else value
        for (kwarg, value) in kwargs.items()
    }

    return func(clip, *new_args, **new_kwargs)
