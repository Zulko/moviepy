"""Defines the base class for all effects in MoviePy."""

import copy as _copy
from abc import ABCMeta, abstractmethod

from moviepy.Clip import Clip


# 效果
class Effect(metaclass=ABCMeta):
    """MoviePy 中所有效果的基抽象类。
    任何新的效果都必须继承这个基类。
    """

    def copy(self):
        """返回 Effect 的浅拷贝。

        在应用效果之前，必须*始终*拷贝一个 ``Effect``，
        因为它们中的一些在应用时会修改自己的属性。
        例如，通过使用目标剪辑的属性来设置先前未设置的属性。

        如果使用原始效果，多次调用相同的效果可能会导致不同的属性，
        以及等效剪辑的不同结果。

        通过使用拷贝，我们可以确保多次使用相同的效果对象，同时保持相同的行为/结果。

        在某种程度上，拷贝使效果本身具有幂等性。
        """
        return _copy.copy(self)

    @abstractmethod
    def apply(self, clip: Clip) -> Clip:
        """
        在剪辑上应用当前效果

        参数
        ----------
        clip
            要应用效果的目标剪辑。
            （在内部，MoviePy 将始终传递原始剪辑的拷贝）
        """

        pass
