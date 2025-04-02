from dataclasses import dataclass

from moviepy.Effect import Effect


@dataclass
class AccelDecel(Effect):
    """
    加速和减速剪辑，适用于制作 GIF。

    参数
    ----------
    new_duration : float
      新转换剪辑的持续时间。如果为 None，则为当前剪辑的持续时间。

    abruptness : float
      加速-减速函数中的斜率形状。它将取决于参数的值：

      * ``-1 < abruptness < 0``：加速，减速，加速。
      * ``abruptness == 0``：无效果。
      * ``abruptness > 0``：减速，加速，减速。

    soonness : float
      对于正的 abruptness，确定转换发生的早晚。
      应为正数。

    引发
    ------
    ValueError
      当 ``soonness`` 参数小于 0 时。

    例子
    --------
    以下图表显示了不同参数组合生成的函数，其中斜率的值表示生成的视频的速度，
    线性函数（红色）是不产生任何转换的组合。

    .. image:: /_static/medias/accel_decel-fx-params.png
      :alt: acced_decel FX 参数组合
    """

    new_duration: float = None
    abruptness: float = 1.0
    soonness: float = 1.0

    def _f_accel_decel(
        self, t, old_duration, new_duration, abruptness=1.0, soonness=1.0
    ):
        a = 1.0 + abruptness

        def _f(t):
            def f1(t):
                return (0.5) ** (1 - a) * (t**a)

            def f2(t):
                return 1 - f1(1 - t)

            return (t < 0.5) * f1(t) + (t >= 0.5) * f2(t)

        return old_duration * _f((t / new_duration) ** soonness)

    def apply(self, clip):
        """Apply the effect to the clip."""
        if self.new_duration is None:
            self.new_duration = clip.duration

        if self.soonness < 0:
            raise ValueError("'sooness' should be a positive number")

        return clip.time_transform(
            lambda t: self._f_accel_decel(
                t=t,
                old_duration=clip.duration,
                new_duration=self.new_duration,
                abruptness=self.abruptness,
                soonness=self.soonness,
            )
        ).with_duration(self.new_duration)
