from moviepy import *
import numpy as np

# Random RGB noise image of 200x100
noise_image = np.random.randint(low=0, high=255, size=(100, 200, 3))

myclip1 = ImageClip("example.png")  # You can create it from a path
myclip2 = ImageClip(noise_image)  # from a (height x width x 3) RGB numpy array
myclip3 = VideoFileClip("./example.mp4").to_ImageClip(
    t="00:00:01"
)  # Or load videoclip and extract frame at a given time
