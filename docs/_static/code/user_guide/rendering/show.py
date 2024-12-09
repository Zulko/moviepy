from moviepy import *

myclip = VideoFileClip("./example.mp4")

# We show the first frame of our clip
myclip.show()

# We show the frame at point 00:00:01.5 of our clip
myclip.show(1.5)

# We want to see our clip without applying his mask
myclip.show(1.5, with_mask=False)
