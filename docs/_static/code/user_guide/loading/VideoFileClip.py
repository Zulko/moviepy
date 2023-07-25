from moviepy import *

myclip = VideoFileClip("example.mp4")

# video file clips already have fps and duration
print('Clip duration: {}'.format(myclip.duration)) 
print('Clip fps: {}'.format(myclip.fps))

myclip = myclip.with_subclip(5, 10) # Cutting the clip between 5 and 10 secs. 
print('Clip duration: {}'.format(myclip.duration)) # Cuting will update duration
print('Clip fps: {}'.format(myclip.fps)) # and keep fps

myclip.write_videofile("result.mp4") # the output video will be 5 sec long and use original fps