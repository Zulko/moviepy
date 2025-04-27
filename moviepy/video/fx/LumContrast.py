from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class LumContrast(Effect):
    """ 剪辑的亮度对比度校正。"""

    lum: float = 0,              # 整体亮度增减（+变亮，-变暗）
    contrast: float = 0,         # 对比度调整（+增强明暗差异，-减弱）
    contrast_threshold: float = 127  # 对比度参考基准（默认是中灰色）

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""

        def image_filter(im):
            im = 1.0 * im  # float conversion
            corrected = (
                im + self.lum + self.contrast * (im - float(self.contrast_threshold))
            )
            corrected[corrected < 0] = 0
            corrected[corrected > 255] = 255
            return corrected.astype("uint8")

        return clip.image_transform(image_filter)
