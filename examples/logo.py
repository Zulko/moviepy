import numpy as np

from moviepy import *


w, h = moviesize = (720, 380)

duration = 1


def f(t, size, a=np.pi / 3, thickness=20):  # noqa D103
    w, h = size
    v = thickness * np.array([np.cos(a), np.sin(a)])[::-1]
    center = [int(t * w / duration), h / 2]
    return biGradientScreen(size, center, v, 0.6, 0.0)


logo = ImageClip("../../videos/logo_descr.png").resize(width=w / 2).with_mask(mask)

screen = logo.on_color(moviesize, color=(0, 0, 0), pos="center")

shade = ColorClip(moviesize, color=(0, 0, 0))
mask_frame = lambda t: f(t, moviesize, duration)
shade.mask = VideoClip(is_mask=True, get_frame=mask_frame)

cc = CompositeVideoClip([im.set_pos(2 * ["center"]), shade], size=moviesize)

cc.subclip(0, duration).write_videofile("moviepy_logo.avi", fps=24)
