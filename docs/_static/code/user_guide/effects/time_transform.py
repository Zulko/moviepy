from moviepy import VideoFileClip
import math

my_clip = VideoFileClip("example.mp4")

# Let's accelerate the video by a factor of 3
modified_clip1 = my_clip.time_transform(lambda t: t * 3)
# Let's play the video back and forth with a "sine" time-warping effect
modified_clip2 = my_clip.time_transform(lambda t: 1 + math.sin(t))
