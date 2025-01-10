"""In this example, we will concatenate two clips with a 1-second
crossfadein of the second clip."""

from moviepy import VideoFileClip, CompositeVideoClip, vfx

# We load all the clips we want to compose
clip1 = VideoFileClip("example.mp4")
clip2 = VideoFileClip("example2.mp4")

clips = [
    clip1.with_end(2),
    clip2.with_start(1).with_effects([vfx.CrossFadeIn(1)]),
]
final_clip = CompositeVideoClip(clips)
final_clip.write_videofile("final_clip.mp4")
