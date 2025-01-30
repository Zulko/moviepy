from moviepy import *

# By default an ImageClip has no duration
my_clip = ImageClip("example.png")

try:
    # This will fail! We cannot write a clip with no duration!
    my_clip.write_videofile("result.mp4")
except:
    print("Cannot write a video without duration")

# By calling with_duration on our clip, we fix the problem! We also need to set fps
my_clip.with_duration(2).write_videofile("result.mp4", fps=1)
