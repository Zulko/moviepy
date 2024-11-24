from moviepy import VideoFileClip

myclip = VideoFileClip("example.mp4")

# video file clips already have fps and duration
print("Clip duration: {}".format(myclip.duration))
print("Clip fps: {}".format(myclip.fps))

myclip = myclip.subclipped(0.5, 2)  # Cutting the clip between 0.5 and 2 secs.
print("Clip duration: {}".format(myclip.duration))  # Cuting will update duration
print("Clip fps: {}".format(myclip.fps))  # and keep fps
# the output video will be 1.5 sec long and use original fps
myclip.write_videofile("result.mp4")
