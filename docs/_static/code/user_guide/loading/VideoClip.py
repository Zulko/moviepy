from PIL import Image, ImageDraw
import numpy as np
from moviepy import VideoClip
import math

WIDTH, HEIGHT = (128, 128)
RED = (255, 0, 0)


def frame_function(t):
    frequency = 1  # One pulse per second
    coef = 0.5 * (1 + math.sin(2 * math.pi * frequency * t))  # radius varies over time
    radius = WIDTH * coef

    x1 = WIDTH / 2 - radius / 2
    y1 = HEIGHT / 2 - radius / 2
    x2 = WIDTH / 2 + radius / 2
    y2 = HEIGHT / 2 + radius / 2

    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    draw.ellipse((x1, y1, x2, y2), fill=RED)

    return np.array(img)  # returns a 8-bit RGB array


# we define a 2s duration for the clip to be able to render it later
clip = VideoClip(frame_function, duration=2)
# we must set a framerate because VideoClip have no framerate by default
clip.write_gif("circle.gif", fps=15)
