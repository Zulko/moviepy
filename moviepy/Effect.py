"""Defines the base class for all effects in MoviePy."""

import copy as _copy
from abc import ABCMeta, abstractmethod

from moviepy.Clip import Clip


class Effect(metaclass=ABCMeta):
    """Base abstract class for all effects in MoviePy.
    Any new effect have to extend this base class.
    """

    def copy(self):
        """Return a shallow copy of an Effect.

        You must *always* copy an ``Effect`` before applying,
        because some of them will modify their own attributes when applied.
        For example, setting a previously unset property by using target clip property.

        If we was to use the original effect, calling the same effect multiple times
        could lead to different properties, and different results for equivalent clips.

        By using copy, we ensure we can use the same effect object multiple times while
        maintaining the same behavior/result.

        In a way, copy makes the effect himself being kind of idempotent.
        """
        return _copy.copy(self)

    @abstractmethod
    def apply(self, clip: Clip) -> Clip:
        """Apply the current effect on a clip

        Parameters
        ----------
        clip
            The target clip to apply the effect on.
            (Internally, MoviePy will always pass a copy of the original clip)

        """
        pass
