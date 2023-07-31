from moviepy import *

myclip = VideoFileClip("example.mp4")

# video file clips already have fps and duration
print("Clip duration: {}".format(myclip.duration))
print("Clip fps: {}".format(myclip.fps))

myclip = myclip.with_subclip(0.5, 2)  # Cutting the clip between 0.5 and 2 secs.
print("Clip duration: {}".format(myclip.duration))  # Cuting will update duration
print("Clip fps: {}".format(myclip.fps))  # and keep fps

myclip.write_videofile(
    "result.mp4"
)  # the output video will be 1.5 sec long and use original fps
