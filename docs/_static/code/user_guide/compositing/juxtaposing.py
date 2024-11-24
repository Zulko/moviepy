"""Let's juxtapose four video clips in a 2x2 grid."""

from moviepy import VideoFileClip, clips_array, vfx

# We will use the same clip and transform it in 3 ways
clip1 = VideoFileClip("example.mp4").with_effects([vfx.Margin(10)])  # add 10px contour
clip2 = clip1.with_effects([vfx.MirrorX()])  # Flip horizontaly
clip3 = clip1.with_effects([vfx.MirrorY()])  # Flip verticaly
clip4 = clip1.resized(0.6)  # downsize to 60% of original

# The form of the final clip will depend of the shape of the array
# We want our clip to be our 4 videos, 2x2, so we make an array of 2x2
array = [
    [clip1, clip2],
    [clip3, clip4],
]
final_clip = clips_array(array)
# let's resize the final clip so it has 480px of width
final_clip = final_clip.resized(width=480)

final_clip.write_videofile("final_clip.mp4")
