from moviepy import *

# We load all the clips we want to compose
clip1 = VideoFileClip("example.mp4")
clip2 = VideoFileClip("exampl2.mp4").with_subclip(50,60)

# Clip2 will be on top of clip1 for 1s
clip1 = clip1.with_end(6)
clip2 = clip2.with_start(5)

# We will add a crossfadein on clip2 for 1s
# As the other effects, transitions are added to Clip methods at runtime 
clip2 = clip2.crossfadein(1) 



# We write the result
final_clip = CompositeVideoClip([clip1, clip2])
final_clip.write_videofile("final_clip.mp4")