from moviepy import *

# We load all the clips we want to compose
clip1 = VideoFileClip("example.mp4")
clip2 = VideoFileClip("example2.mp4").with_subclip(0, 1)

# Clip2 will be on top of clip1 for 1s
clip1 = clip1.with_end(2)
clip2 = clip2.with_start(1)

# We will add a crossfadein on clip2 for 1s
# As the other effects, transitions are added to Clip methods at runtime
clip2 = clip2.with_effects([vfx.CrossFadeIn(1)])


# We write the result
final_clip = CompositeVideoClip([clip1, clip2])
final_clip.write_videofile("final_clip.mp4")
