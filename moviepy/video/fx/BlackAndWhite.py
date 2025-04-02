from dataclasses import dataclass

import numpy as np

from moviepy.Effect import Effect


@dataclass
class BlackAndWhite(Effect):
    """
    对图像进行去饱和处理，使其变为黑白。
    参数 RGB 允许设置不同颜色通道的权重。
    如果 RGB 为 'CRT_phosphor'，则使用一组特殊的值。
    preserve_luminosity 保持 RGB 的总和为 1。
    """

    RGB: str = None
    preserve_luminosity: bool = True

    def apply(self, clip):
        """Apply the effect to the clip."""
        if self.RGB is None:
            self.RGB = [1, 1, 1]

        if self.RGB == "CRT_phosphor":
            self.RGB = [0.2125, 0.7154, 0.0721]

        R, G, B = (
            1.0
            * np.array(self.RGB)
            / (sum(self.RGB) if self.preserve_luminosity else 1)
        )

        def filter(im):
            im = R * im[:, :, 0] + G * im[:, :, 1] + B * im[:, :, 2]
            return np.dstack(3 * [im]).astype("uint8")

        return clip.image_transform(filter)
