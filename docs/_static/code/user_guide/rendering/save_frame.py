from moviepy import *

# We load all the clips we want to compose
myclip = VideoFileClip("example.mp4")
myclip.save_frame("result.png", t=5) # Save frame at 5 sec
