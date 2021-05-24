"""Decorators used by moviepy."""
import inspect
import os

import decorator

from moviepy.tools import convert_to_seconds


@decorator.decorator
def outplace(func, clip, *args, **kwargs):
    """Applies ``func(clip.copy(), *args, **kwargs)`` and returns ``clip.copy()``."""
    new_clip = clip.copy()
    func(new_clip, *args, **kwargs)
    return new_clip


@decorator.decorator
def convert_masks_to_RGB(func, clip, *args, **kwargs):
    """If the clip is a mask, convert it to RGB before running the function."""
    if clip.is_mask:
        clip = clip.to_RGB()
    return func(clip, *args, **kwargs)


@decorator.decorator
def apply_to_mask(func, clip, *args, **kwargs):
    """Applies the same function ``func`` to the mask of the clip created with
    ``func``.
    """
    new_clip = func(clip, *args, **kwargs)
    if getattr(new_clip, "mask", None):
        new_clip.mask = func(new_clip.mask, *args, **kwargs)
    return new_clip


@decorator.decorator
def apply_to_audio(func, clip, *args, **kwargs):
    """Applies the function ``func`` to the audio of the clip created with ``func``."""
    new_clip = func(clip, *args, **kwargs)
    if getattr(new_clip, "audio", None):
        new_clip.audio = func(new_clip.audio, *args, **kwargs)
    return new_clip


@decorator.decorator
def requires_duration(func, clip, *args, **kwargs):
    """Raises an error if the clip has no duration."""
    if clip.duration is None:
        raise ValueError("Attribute 'duration' not set")
    else:
        return func(clip, *args, **kwargs)


@decorator.decorator
def requires_fps(func, clip, *args, **kwargs):
    """Raises an error if the clip has no fps."""
    if not hasattr(clip, "fps") or clip.fps is None:
        raise ValueError("Attribute 'fps' not set")
    else:
        return func(clip, *args, **kwargs)


@decorator.decorator
def audio_video_fx(func, clip, *args, **kwargs):
    """Use an audio function on a video/audio clip.

    This decorator tells that the function func (audioclip -> audioclip)
    can be also used on a video clip, at which case it returns a
    videoclip with unmodified video and modified audio.
    """
    if hasattr(clip, "audio"):
        new_clip = clip.copy()
        if clip.audio is not None:
            new_clip.audio = func(clip.audio, *args, **kwargs)
        return new_clip
    else:
        return func(clip, *args, **kwargs)


def preprocess_args(fun, varnames):
    """Applies fun to variables in varnames before launching the function."""

    def wrapper(func, *args, **kwargs):
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


def convert_parameter_to_seconds(varnames):
    """Converts the specified variables to seconds."""
    return preprocess_args(convert_to_seconds, varnames)


def convert_path_to_string(varnames):
    """Converts the specified variables to a path string."""
    return preprocess_args(os.fspath, varnames)


@decorator.decorator
def add_mask_if_none(func, clip, *args, **kwargs):
    """Add a mask to the clip if there is none."""
    if clip.mask is None:
        clip = clip.add_mask()
    return func(clip, *args, **kwargs)


@decorator.decorator
def use_clip_fps_by_default(func, clip, *args, **kwargs):
    """Will use ``clip.fps`` if no ``fps=...`` is provided in **kwargs**."""

    def find_fps(fps):
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
