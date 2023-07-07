import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def headblur(clip, fx, fy, radius, intensity=None):
    """Returns a filter that will blur a moving part (a head ?) of the frames.

    The position of the blur at time t is defined by (fx(t), fy(t)), the radius
    of the blurring by ``radius`` and the intensity of the blurring by ``intensity``.
    """
    if intensity is None:
        intensity = int(2 * radius / 3)

    def filter(gf, t):
        im = gf(t).copy()
        h, w, d = im.shape
        x, y = int(fx(t)), int(fy(t))
        x1, x2 = max(0, x - radius), min(x + radius, w)
        y1, y2 = max(0, y - radius), min(y + radius, h)

        image = Image.fromarray(im)
        mask = Image.new('RGB', image.size)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([x1, y1, x2, y2],fill=(255,255,255))

        blurred = image.filter(ImageFilter.GaussianBlur(radius=15))

        res = np.where(np.array(mask) > 0, np.array(blurred), np.array(image)) 
        return res

    return clip.transform(filter)