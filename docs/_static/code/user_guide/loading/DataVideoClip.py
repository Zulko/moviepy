"""Let's make a clip where frames depend on values in a list"""

from moviepy import DataVideoClip
import numpy as np

# Dataset will just be a list of colors as RGB
dataset = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (0, 255, 255),
    (255, 0, 255),
    (255, 255, 0),
]


# The function make frame take data and create an image of 200x100 px
# filled with the color given in the dataset
def frame_function(data):
    frame = np.full((100, 200, 3), data, dtype=np.uint8)
    return frame


# We create the DataVideoClip, and we set FPS at 2, making a 3s clip
# (because len(dataset) = 6, so 6/2=3)
myclip = DataVideoClip(data=dataset, data_to_frame=frame_function, fps=2)

# Modifying fps here will change video FPS, not clip FPS
myclip.write_videofile("result.mp4", fps=30)
