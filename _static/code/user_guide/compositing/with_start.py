from moviepy import VideoFileClip, CompositeVideoClip

# We load all the clips we want to compose
clip1 = VideoFileClip("example.mp4")
clip2 = VideoFileClip("example2.mp4").subclipped(0, 1)
clip3 = VideoFileClip("example3.mp4")

# We want to stop clip1 after 1s
clip1 = clip1.with_end(1)

# We want to play clip2 after 1.5s
clip2 = clip2.with_start(1.5)

# We want to play clip3 at the end of clip2, and so for 3 seconds only
# Some times its more practical to modify the duration of a clip instead
# of his end
clip3 = clip3.with_start(clip2.end).with_duration(1)

# We write the result
final_clip = CompositeVideoClip([clip1, clip2, clip3])
final_clip.write_videofile("final_clip.mp4")
