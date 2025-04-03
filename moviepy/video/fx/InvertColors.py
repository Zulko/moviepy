from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class InvertColors(Effect):
    """返回颜色反转的剪辑。

    对于遮罩，所有像素的值都替换为（255-v）或（1-v
    黑色变成白色，绿色变成紫色，等等。
    """

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        maxi = 1.0 if clip.is_mask else 255
        return clip.image_transform(lambda f: maxi - f)
