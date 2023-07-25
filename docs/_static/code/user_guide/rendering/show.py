from moviepy import *

myclip = VideoFileClip('./example.mp4')

# We show the first frame of our clip
myclip.show()

# We show the frame at point 00:00:30 of our clip
myclip.show(30)

# We want to see our clip without applying his mask
myclip.preview(30, with_mask=False)
