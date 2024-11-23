from moviepy import *

# We load all the clips we want to compose
clip1 = VideoFileClip("example.mp4")
clip2 = VideoFileClip("example2.mp4").with_subclip(0, 1)
clip3 = VideoFileClip("example3.mp4")

# We concatenate them and write theme stacked on top of each other, with clip3 over clip2 over clip1
final_clip = CompositeVideoClip([clip1, clip2, clip3])
final_clip.write_videofile("final_clip.mp4")
