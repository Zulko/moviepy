from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class Crop(Effect):
    """
    裁剪剪辑以获得一个新剪辑的效果，其中仅保留原始剪辑的矩形子区域。
    `x1,y1` 表示裁剪区域的左上角，`x2,y2` 表示右下角。所有坐标以像素为单位。
    接受浮点数。

    裁剪任意矩形：

    >>> Crop(x1=50, y1=60, x2=460, y2=275)

    仅移除 y=30 上方的部分：

    >>> Crop(y1=30)

    裁剪一个从左边 10 像素开始，宽度为 200 像素的矩形：

    >>> Crop(x1=10, width=200)

    裁剪一个以 x,y=(300,400) 为中心，宽度为 50，高度为 150 的矩形：

    >>> Crop(x_center=300, y_center=400, width=50, height=150)

    上述任何组合都应该有效，例如对于这个以 x=300 为中心，具有显式 y 边界的矩形：

    >>> Crop(x_center=300, width=400, y1=100, y2=600)
    """

    x1: int = None
    y1: int = None
    x2: int = None
    y2: int = None
    width: int = None
    height: int = None
    x_center: int = None
    y_center: int = None

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        if self.width and self.x1 is not None:
            self.x2 = self.x1 + self.width
        elif self.width and self.x2 is not None:
            self.x1 = self.x2 - self.width

        if self.height and self.y1 is not None:
            self.y2 = self.y1 + self.height
        elif self.height and self.y2 is not None:
            self.y1 = self.y2 - self.height

        if self.x_center:
            self.x1, self.x2 = (
                self.x_center - self.width / 2,
                self.x_center + self.width / 2,
            )

        if self.y_center:
            self.y1, self.y2 = (
                self.y_center - self.height / 2,
                self.y_center + self.height / 2,
            )

        self.x1 = self.x1 or 0
        self.y1 = self.y1 or 0
        self.x2 = self.x2 or clip.size[0]
        self.y2 = self.y2 or clip.size[1]

        return clip.image_transform(
            lambda frame: frame[
                int(self.y1) : int(self.y2), int(self.x1) : int(self.x2)
            ],
            apply_to=["mask"],
        )
