"""Let's invert the green and blue channels of a video."""

from moviepy import VideoFileClip
import numpy

my_clip = VideoFileClip("example.mp4")


def invert_green_blue(image: numpy.ndarray) -> numpy.ndarray:
    return image[:, :, [0, 2, 1]]


modified_clip1 = my_clip.image_transform(invert_green_blue)
