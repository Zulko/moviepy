from moviepy import VideoFileClip
import math

my_clip = VideoFileClip("example.mp4")


# You can define a function the classical way
def accel_x3(time: float) -> float:
    return time * 3


modified_clip1 = my_clip.time_transform(accel_x3)

# Of you can also use lambda function
modified_clip2 = my_clip.time_transform(lambda t: 1 + math.sin(t))
