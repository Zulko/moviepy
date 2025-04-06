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
    """
    所有剪辑（视频剪辑和音频剪辑）的基类。
    属性
    ----------
    start : 当剪辑包含在合成中时，剪辑开始播放的合成时间（以秒为单位）。
    end : 当剪辑包含在合成中时，剪辑停止播放的合成时间（以秒为单位）。
    duration : 剪辑的持续时间（以秒为单位）。有些剪辑是无限的，在这种情况下，它们的持续时间将为“无”。
    """

    # 所有临时视频和音频文件的前缀。
    # 您可以使用以下方式覆盖它
    # >>> Clip._TEMP_FILES_PREFIX = "temp_"
    _TEMP_FILES_PREFIX = "TEMP_MPY_"

    def __init__(self):
        self.start = 0
        self.end = None
        self.duration = None

        self.memoize = False  # 表示是否启用记忆化，用于优化剪辑的处理过程。记忆化的意思是缓存已经处理过的结果，避免重复计算。
        self.memoized_t = None
        self.memoized_frame = None
        # 这两个属性用于存储记忆化的时间和帧数据。它们通常用于优化视频剪辑的渲染和计算过程，减少不必要的重复计算。

    def copy(self):
        """ 允许在剪辑中使用“.copy()”作为链式方法调用。
        剪辑对象上使用 .copy() 来创建剪辑的副本。这意味着你可以在不修改原始剪辑的情况下，对剪辑进行修改和操作
        """
        return _copy.copy(self)

    @convert_parameter_to_seconds(["t"])
    def get_frame(
            self,
            t  # 浮点数或元组或字符串, 将返回其帧的剪辑的时刻。
    ):
        """
        用于获取剪辑在某一时刻 t 的帧。它返回的是一个 numpy 数组，表示在该时刻该剪辑的 RGB 图像。
        对于音频剪辑，它返回的是该时刻的音频值（单声道或立体声）。
        """

        # 即将推出：此时进行调试的智能错误处理 (官方注释)
        if self.memoize:
            # memoization（缓存）：方法使用了缓存机制。如果你在多次调用 get_frame(t) 时传入相同的 t，它会返回缓存的帧，从而提高性能。
            # 如果已经计算过某个时刻 t 的帧，就不会重新计算，而是直接返回之前计算的结果。
            if t == self.memoized_t:
                return self.memoized_frame
            else:
                frame = self.frame_function(t)
                self.memoized_t = t
                self.memoized_frame = frame
                return frame
        else:
            return self.frame_function(t)

    def transform(
            self,
            func,  # 这是一个函数，它接受两个参数：
            # gf：当前剪辑的 get_frame 方法（即获取视频帧的函数）。
            # t：视频的时间（以秒为单位）。
            # frame：是传入的帧（一个 numpy 数组），你可以对这个帧进行修改并返回一个新的帧。
            apply_to=None,  # 你可以选择是否将转换应用到视频剪辑的其它部分（如 mask 或 audio）。它可以是：
            # "mask"：应用于剪辑的遮罩。
            # "audio"：应用于剪辑的音频。
            # ["mask", "audio"]：同时应用于遮罩和音频。
            # 默认为 None，表示只对视频部分进行操作。
            keep_duration=True  # 设置为 True，表示转换后的剪辑的持续时间保持不变。如果设置为 False，转换后的剪辑的持续时间可能会根据帧的处理发生变化。
    ):
        """
        通用的处理函数

        允许你对 Clip 对象（如 VideoClip 或 ImageClip）的帧进行转化处理，返回一个新的 Clip 对象，处理过程通过你提供的转换函数 func 来实现。
        这个方法可以用来做一些复杂的视频帧处理，如视频滤镜、特效、图像变换等。

        剪辑的常规处理。 返回一个新的剪辑，其帧是一个变换 （通过函数``func``）当前剪辑的帧。
        Examples
        --------
        在以下“new_clip”中，有一个 100 像素高的剪辑，其视频内容以每秒 50 像素的速度从“clip”帧的顶部滚动到底部。
        >>> filter = lambda get_frame,t : get_frame(t)[int(t):int(t)+50, :]
        >>> new_clip = clip.transform(filter, apply_to='mask')
        """

        '''
        解释：
        apply_to 默认值 []（如果没有传递），使用 with_updated_frame_function 更新帧函数，生成一个新的 Clip 对象。
        如果 apply_to 指定了 mask 或 audio，该方法会递归地将变换函数应用于视频剪辑的遮罩或音频部分（如果存在）。
        最后，方法返回一个新的剪辑对象，该对象的帧是通过 func 转换过的。
        '''
        if apply_to is None:
            apply_to = []

        # mf = copy(self.frame_function)
        new_clip = self.with_updated_frame_function(lambda t: func(self.get_frame, t))

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

    def time_transform(
            self,
            time_func,
            # 这是一个函数，接受一个时间参数 t（视频播放的当前时间，单位为秒），并返回一个新的时间值 new_t。这个新时间值将替代原时间 t，用来决定该时间点的视频帧、音频帧等。
            # 比如，time_func(t) = 2*t 表示将时间轴加速，所有的时间点都会被加速两倍。
            # 另外，time_func(t) = 3-t 可以用来做倒放，视频的播放时间会反向。
            apply_to=None,
            # 指定是否将时间变换应用到遮罩和音频部分。它可以是：
            # "mask"：只应用于视频的遮罩。
            # "audio"：只应用于音频部分。
            # ["mask", "audio"]：同时应用于视频的遮罩和音频。
            #
            # 默认值是 None，只应用于视频内容。
            keep_duration=False  # 果设置为 True，表示变换后剪辑的持续时间保持不变。如果设置为 False，剪辑的持续时间可能会因为时间轴变换而变化。
    ):
        """
        用于修改剪辑时间轴的功能。它通过接受一个时间函数 time_func，并将时间 t 替换为 time_func(t)，从而改变视频、音频或遮罩的播放时间。
        这个方法可以用来做一些特殊的时间轴变换，例如加速、倒放、延迟等。

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

        # TODO 这里返回的 duration 是None，明天再看看
        return self.transform(
            lambda get_frame, t: get_frame(time_func(t)),
            apply_to,
            keep_duration=keep_duration,
        )

    def with_effects(
            self,
            effects: List["Effect"]  # 这是一个包含 Effect 对象的列表。你可以将多个特效传递给该方法，每个特效会依次应用到当前剪辑。
    ):
        """ 返回当前剪辑的副本，并应用效果
        >>> new_clip = clip.with_effects([vfx.Resize(0.2, method="bilinear")])

        您还可以将多个效果作为列表传递
        >>> clip.with_effects([afx.VolumeX(0.5), vfx.Resize(0.3), vfx.Mirrorx()])
        """
        '''
        允许你在剪辑上应用多个特效，并且通过链式调用的方式保持代码简洁。
        你可以通过传入一系列 Effect 对象（如视频尺寸调整、音量控制、视频翻转等），将这些特效组合应用到视频上，生成一个全新的视频剪辑。
        '''
        new_clip = self.copy()
        for effect in effects:
            # 我们总是在使用效果之前先复制它，请参阅 Effect.copy
            # 以了解为什么我们需要
            effect_copy = effect.copy()
            new_clip = effect_copy.apply(new_clip)

        return new_clip

    @apply_to_mask
    @apply_to_audio
    @convert_parameter_to_seconds(["t"])
    @outplace
    def with_start(
            self,
            t,  # 浮点数或元组或字符串 剪辑的新“start”属性值。
            change_end=True
            # 指示是否必须相应地更改“end "属性值，
            # 如果``change_end=True``且剪辑具有``持续时间`` 属性，则剪辑的“end "属性将更新为`开始+持续时间``。
            # 如果``change_end=False``且剪辑具有 "end"属性，剪辑的"duration"属性将为 更新为“结束-开始”。
    ):
        """
        返回剪辑的副本，其中 ``start`` 属性设置为 ``t``，可以用秒 (15.35)、(分，秒)、
        (时，分，秒) 或字符串表示：'01:03:05.35'。
        如果存在，这些更改也适用于当前剪辑的 ``audio`` 和 ``mask`` 剪辑。

        注意：
        剪辑的开始和结束属性定义剪辑在合成视频剪辑中使用时何时开始播放，而不是剪辑本身的开始时间。
        即：with_start(10) 表示剪辑仍将从第一帧开始，
        但如果在合成视频剪辑中使用，它将仅在 10 秒后开始显示。
        """
        '''
        主要用于修改剪辑在复合视频中的起始时间，而不改变剪辑本身的时间轴。你可以通过这个方法来调整视频剪辑的相对位置，确保其在复合视频中的播放顺序。
        change_end 参数允许你决定是否同时调整结束时间，或者根据需要仅调整开始时间而不改变剪辑的总持续时间。
        '''
        self.start = t
        if (self.duration is not None) and change_end:
            self.end = t + self.duration
        elif self.end is not None:
            self.duration = self.end - self.start

    @apply_to_mask
    @apply_to_audio
    @convert_parameter_to_seconds(["t"])
    @outplace
    def with_end(
            self,
            t  # t, # 浮点数或元组或字符串 剪辑的新“结束”属性值。
    ):
        """
        返回剪辑的副本，其中 ``end`` 属性设置为 ``t``，可以以秒 (15.35)、（分，秒）、
        （时，分，秒）或字符串表示：'01:03:05.35'。还设置返回剪辑的掩码和音频（如果有）的持续时间。

        注意：
        剪辑的开始和结束属性定义剪辑在合成视频剪辑中使用时开始播放的时间，而不是剪辑本身的开始时间。
        即：with_start(10) 表示剪辑仍将从第一帧开始，
        但如果在合成视频剪辑中使用，它将仅在 10 秒后开始显示。
        """
        '''
        用来设置视频剪辑的 结束时间 的，并返回一个新的剪辑副本。它和我们刚学的 with_start 方法属于一对“时间管理”工具
        核心作用就是控制 在合成视频中，剪辑何时结束播放。
        '''
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
    def with_duration(
            self,
            duration,  # 新的时长值（单位：秒）。
            change_end=True
            # True：end 值会被设置为 start + duration（自动调整 end）。
            # False：保持 end 不变，而调整 start 以确保 end - start = duration。
    ):
        """
        返回剪辑的一个副本，并将其 duration（时长）属性设置为 t。
        t
        可以用秒（如 15.35）、
        分钟和秒（如 (1, 30)）、
        小时分钟秒（如 (1, 3, 5)）
        或者字符串格式（如 '01:03:05.35'）表示。

        如果剪辑包含 蒙版（mask） 或 音频（audio），它们的时长也会被同步修改。
        如果 change_end=False，则 start 属性会根据新的 duration 及剪辑原本的 end 值进行调整。
        """
        self.duration = duration

        if change_end:
            self.end = None if (duration is None) else (self.start + duration)
        else:
            if self.duration is None:
                raise ValueError("Cannot change clip start when new duration is None")
            self.start = self.end - duration

    @outplace
    def with_updated_frame_function(
            self,
            frame_function  # 它是一个函数，定义了「在任意时间点 t，当前帧画面长啥样」。
            #         frame_function(t: float) -> np.ndarray（图像）
            #         它是 clip 在时间轴上如何生成画面的核心逻辑。
    ):
        """设置剪辑的"frame_function"属性。用于设置任意/复杂的视频剪辑。

        Parameters
        ----------

        frame_function : 新的帧创建器功能的剪辑。

        方法	                                     作用	                    复杂性	        推荐使用
        transform(func)	                    包装原来的 get_frame，做变换	    更方便	        90% 场景
        with_updated_frame_function(func)	完全替换原始帧生成方式	            灵活但更底层	    高级用法、动态绘图等

        """
        self.frame_function = frame_function

    def with_fps(
            self,
            fps,  # int 剪辑的新“fps”属性值。
            change_duration=False
            # 如果“change_duration=True”，则视频速度将更改为与新的 fps 匹配（所有帧以 1:1 的比例保存）。例如，如果在此模式下 fps 减半，则持续时间将加倍。
    ):
        """ 返回剪辑的副本，并使用新的默认fps，write_videofile、iterframe等。"""
        if change_duration:
            from moviepy.video.fx.MultiplySpeed import MultiplySpeed

            newclip = self.with_effects([MultiplySpeed(fps / self.fps)])
        else:
            newclip = self.copy()

        newclip.fps = fps
        return newclip

    @outplace
    def with_is_mask(
            self,
            is_mask  # 剪辑的新“is_mask”属性值。
    ):
        """ 设置该剪辑是否为蒙版。"""
        self.is_mask = is_mask

    @outplace
    def with_memoize(
            self,
            memoize  # bool 指示剪辑是否应在内存中保留最后读取的帧。
    ):
        """ 设置剪辑是否应在内存中保留最后读取的帧。"""
        self.memoize = memoize

    @convert_parameter_to_seconds(["start_time", "end_time"])
    @apply_to_mask
    @apply_to_audio
    # 这些装饰器确保如果 self 有 mask（蒙版）或 audio（音频），那么截取的 mask 和 audio 也会相应调整。
    def subclipped(
            self,
            start_time=0,  # 浮点数或元组或字符串，可选。 将选择为生成剪辑的开头的时刻。如果为负数，则将其重置为“clip.duration + start_time”。
            end_time=None
            # 浮点数或元组或字符串，可选。 选择为所生成剪辑的结束时刻。如果未提供，则假定为剪辑的持续时间（可能为无限）。如果为负数，则将其重置为“clip.duration + end_time”。
    ):
        """
            返回在时间“start_time”和“end_time”之间播放当前剪辑内容的剪辑，
            可以用秒（15.35）、（分钟，秒）、（小时，分钟，秒）或字符串表示：'01:03:05.35'。

            如果存在，则生成的子剪辑的“mask”和“audio”将是原始剪辑的“mask”和“audio”的子剪辑。
            相当于将剪辑切片为序列，例如“clip[t_start:t_end]”。
        例如：
            >>> # 剪切剪辑的最后两秒：
            >>> new_clip = clip.subclipped(0, -2)
            如果提供了“end_time”或剪辑具有持续时间属性，则自动设置返回剪辑的持续时间。
        """
        if start_time < 0:
            # 使其更像Python，负值表示移动。 从剪辑的结尾向后
            start_time = self.duration + start_time  # 记住start_time为负数

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
            # 允许稍微容忍一点，以解决舍入错误
            if (self.duration is not None) and (end_time - self.duration > 0.00000001):
                raise ValueError(
                    "end_time (%.02f) " % end_time
                    + "should be smaller or equal to the clip's "
                    + "duration (%.02f)." % self.duration
                )

            new_clip.duration = end_time - start_time
            new_clip.end = new_clip.start + new_clip.duration

        return new_clip

    @convert_parameter_to_seconds(["start_time", "end_time"])
    def with_section_cut_out(
            self,
            start_time,  # （float / tuple / str） 表示从哪个时间点开始删除（从 start_time 开始，该时间之后的视频片段将被移除）。
            end_time  # （float / tuple / str） 表示在哪个时间点结束删除（删除到 end_time 这个时间点）。
    ):
        """
        返回播放当前剪辑内容的剪辑，但会跳过“start_time”和“end_time”之间的摘录，可以以秒（15.35）、
        （分钟，秒）、（小时，分钟，秒）表示，或以字符串表示：'01:03:05.35'。

        如果原始剪辑设置了“duration”属性，则返回剪辑的持续时间将自动计算为“duration - (end_time - start_time)”。
        如果存在，则生成的剪辑的“audio”和“mask”也将被剪切掉。
        """
        new_clip = self.time_transform(
            lambda t: t + (t >= start_time) * (end_time - start_time),
            apply_to=["audio", "mask"],
        )

        if self.duration is not None:
            return new_clip.with_duration(self.duration - (end_time - start_time))
        else:  # pragma: no cover
            return new_clip

    def with_speed_scaled(
            self,
            factor: float = None,
            final_duration: float = None
    ):
        """
        返回一个以当前剪辑 ``factor`` 倍速度播放的新剪辑。

        这个方法会创建一个当前剪辑的副本，但播放速度会乘以指定的 `factor` 值。
        例如，`factor=2` 会使播放速度加倍，剪辑时长减半；`factor=0.5` 会使播放速度减半，剪辑时长加倍。

        你也可以不指定 `factor`，而是通过 `final_duration` 参数来指定你希望这个加速/减速后的剪辑最终变成多长。 MoviePy 会自动计算出需要的速度因子。

        有关这两个参数（`factor` 和 `final_duration`）的更详细信息和底层逻辑，
        请参阅 ``moviepy.video.fx.MultiplySpeed`` 这个特效类。

        总结:
            with_speed_scaled 方法提供了一种方便的方式来创建原始剪辑的变速版本。
            你可以直接指定速度倍数 (factor)，或者指定希望剪辑播放完毕的总时长 (final_duration)，
            MoviePy 会帮你处理底层的速度计算。它内部调用了 MultiplySpeed 特效，并通过 with_effects 方法应用到剪辑上。
        """
        from moviepy.video.fx.MultiplySpeed import MultiplySpeed

        return self.with_effects(
            [MultiplySpeed(factor=factor, final_duration=final_duration)]
        )

    def with_volume_scaled(
            self,
            factor: float,
            start_time=None,
            end_time=None
    ):
        """
        with_volume_scaled 是一个用于调整剪辑音量的便捷方法。它通过 factor 参数控制音量的乘数，
        并且允许使用 start_time 和 end_time 参数来精确控制音量变化的范围。
        这对于需要动态调整音量（比如在特定片段降低背景音乐音量以突出人声）的二次创作场景非常有用。
        它背后依赖的是 moviepy.audio.fx.MultiplyVolume 特效。

        这个方法会创建一个当前剪辑的副本，但是它的音频部分的音量会被调整。
        - `factor` 大于 1.0 会增大音量。
        - `factor` 在 0.0 到 1.0 之间会减小音量。
        - `factor` 等于 0 会使音频静音。
        - `factor` 小于 0 可能会导致未定义的行为或错误，不推荐使用。

        你可以通过可选的 `start_time` 和 `end_time` 参数 (单位是秒) 来指定
        仅在剪辑的某一个时间段内应用这个音量调整效果。
        如果省略 `start_time`，则效果从剪辑开头开始。
        如果省略 `end_time`，则效果一直持续到剪辑结尾。
        如果两者都省略，则音量调整会应用于整个剪辑的音频。
        """
        from moviepy.audio.fx.MultiplyVolume import MultiplyVolume

        return self.with_effects(
            [MultiplyVolume(factor=factor, start_time=start_time, end_time=end_time)]
        )

    @requires_duration
    @use_clip_fps_by_default
    def iter_frames(
            self,
            fps=None,  # int	剪辑迭代的每秒帧数。如果剪辑已经具有“fps”属性，则为可选项。
            with_times=False,  # bool Ff ``True`` 产生 ``(t, frame)`` 的元组，其中 ``t`` 是帧的当前时间，否则仅为 ``frame`` 对象。
            logger=None,  # str 进度条为“bar”，或者为“None”或任何 Proglog 记录器。
            dtype=None  # type 类型转换 Numpy 数组帧。使用图片写入视频、图像时，请使用“dtype="uint8"”。
    ):
        """迭代剪辑的所有帧。
        将剪辑的每一帧作为 HxWxN Numpy 数组返回，其中 N=1 表示蒙版剪辑，N=3 表示 RGB 剪辑。
        此函数并非真正用于视频编辑。它提供了一种简单的方法来逐帧处理视频，适用于科学、计算机视觉等领域...

        Examples
        --------
        .. code:: python
            # 打印剪辑中每帧第一行所含的红色的最大值。
            from moviepy import VideoFileClip
            myclip = VideoFileClip('myvideo.mp4')
            print([frame[0,:,0].max()
                  for frame in myclip.iter_frames()])
        """
        logger = proglog.default_bar_logger(logger)
        for frame_index in logger.iter_bar(
                frame_index=np.arange(0, int(self.duration * fps))
        ):
            # int 用于确保浮点错误被四舍五入为最接近的整数
            t = frame_index / fps

            frame = self.get_frame(t)
            if (dtype is not None) and (frame.dtype != dtype):
                frame = frame.astype(dtype)
            if with_times:
                yield t, frame
            else:
                yield frame

    @convert_parameter_to_seconds(["t"])
    def is_playing(self, t):
        """如果 ``t`` 是时间，则如果 t 在剪辑的开始和结束之间，则返回 true。
        ``t`` 可以以秒 (15.35)、(分，秒)、(时，分，秒) 或字符串表示：'01:03:05.35'。
        如果 ``t`` 是 numpy 数组，则如果剪辑中没有 ``t``，则返回 False，否则返回向量 [b_1, b_2, b_3...]，其中如果 tti 在剪辑中，则 b_i 为 true。
        """
        if isinstance(t, np.ndarray):
            # is the whole list of t outside the clip ?
            tmin, tmax = t.min(), t.max()

            if (self.end is not None) and (tmin >= self.end):
                return False

            if tmax < self.start:
                return False

            # 如果我们到达这里，t的一部分就会落入“clip 剪辑”中
            result = 1 * (t >= self.start)
            if self.end is not None:
                result *= t <= self.end
            return result

        else:
            return (t >= self.start) and ((self.end is None) or (t < self.end))

    def close(self):
        """
        释放所有正在使用的资源。
        #    子类的实现说明：
        #    * 基于内存的资源可以留给垃圾收集器。
        #    * 但是，任何打开的文件都应该关闭，应该被终止。
        #    * 请注意，频繁使用浅拷贝。关闭剪辑可能会影响其副本。
        #    * 因此，不应该由__del__（）调用。
        """
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


if __name__ == '__main__':
    from video.io.VideoFileClip import *

    video = VideoFileClip("../media/chaplin.mp4")
    print("duration", video.duration)
    print("start", video.start)
    print("end", video.end)
    print("memoize", video.memoize)
    print("memoized_t", video.memoized_t)
    print("memoized_frame", video.memoized_frame)
    print("is_mask", video.is_mask)
    print("frame_function", video.frame_function)
