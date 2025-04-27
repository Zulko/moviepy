from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class HeadBlur(Effect):
    """
    返回一个过滤器，该过滤器将模糊帧的移动部分（头部？）。
    时间 t 时的模糊位置由 (fx(t), fy(t)) 定义，模糊半径由“radius”定义，模糊强度由“intensity”定义。
    """

    fx: callable
    fy: callable
    radius: float
    intensity: float = None

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        if self.intensity is None:
            self.intensity = int(2 * self.radius / 3)

        def filter(gf, t):
            im = gf(t).copy()
            h, w, d = im.shape
            x, y = int(self.fx(t)), int(self.fy(t))
            x1, x2 = max(0, x - self.radius), min(x + self.radius, w)
            y1, y2 = max(0, y - self.radius), min(y + self.radius, h)

            image = Image.fromarray(im)
            mask = Image.new("RGB", image.size)
            draw = ImageDraw.Draw(mask)
            draw.ellipse([x1, y1, x2, y2], fill=(255, 255, 255))

            blurred = image.filter(ImageFilter.GaussianBlur(radius=self.intensity))

            res = np.where(np.array(mask) > 0, np.array(blurred), np.array(image))
            return res

        return clip.transform(filter)
