from dataclasses import dataclass

import numpy as np

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class MaskColor(Effect):
    """返回一个新的剪辑，其中原始的剪辑是给定的颜色。

    你也可以通过指定一个非空距离来获得一个“渐进式”遮罩
    门槛，门槛。在这种情况下，如果像素与给定的颜色是d，透明度将是

    d** 刚度/（阈值 ** 刚度+ d** 刚度）

    其在d>>阈值时为1，并且对于d<<阈值为0，通过“刚度”参数化效果
    """

    color: tuple = (0, 0, 0)
    threshold: float = 0
    stiffness: float = 1

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        color = np.array(self.color)

        def hill(x):
            if self.threshold:
                return x**self.stiffness / (
                    self.threshold**self.stiffness + x**self.stiffness
                )
            else:
                return 1.0 * (x != 0)

        def flim(im):
            return hill(np.sqrt(((im - color) ** 2).sum(axis=2)))

        mask = clip.image_transform(flim)
        mask.is_mask = True
        return clip.with_mask(mask)
