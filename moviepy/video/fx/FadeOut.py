from dataclasses import dataclass

import numpy as np

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class FadeOut(Effect):
    """
    使剪辑在剪辑结尾逐渐淡化为某种颜色（默认为黑色），
    持续 ``duration`` 秒。也可以用于遮罩，其中最终颜色必须是 0 到 1 之间的数字。

    对于交叉淡化（一个剪辑在另一个剪辑上逐渐出现或消失），请参阅 ``CrossFadeOut``
    """

    duration: float
    final_color: list = None

    def apply(self, clip: Clip) -> Clip:
        """ 将效果应用于剪辑。 """
        if clip.duration is None:
            raise ValueError("Attribute 'duration' not set")

        if self.final_color is None:
            self.final_color = 0 if clip.is_mask else [0, 0, 0]

        self.final_color = np.array(self.final_color)

        def filter(get_frame, t):
            if (clip.duration - t) >= self.duration:
                return get_frame(t)
            else:
                fading = 1.0 * (clip.duration - t) / self.duration
                return fading * get_frame(t) + (1 - fading) * self.final_color

        return clip.transform(filter)
