from moviepy import *
from moviepy.video.tools.credits import credits1


# Load the mountains clip, cut it, slow it down, make it look darker
clip = (
    VideoFileClip("../../videos/badl-0001.mov", audio=False)
    .subclip(37, 46)
    .speedx(0.4)
    .fx(vfx.colorx, 0.7)
)

# Save the first frame to later make a mask with GIMP (only once)
# ~ clip.save_frame('../../credits/mountainMask2.png')


# Load the mountain mask made with GIMP
mountainmask = ImageClip("../../credits/mountainMask2.png", is_mask=True)

# Generate the credits from a text file
credits = credits1("../../credits/credits.txt", 3 * clip.w / 4)
scrolling_credits = credits.set_pos(lambda t: ("center", -10 * t))


# Make the credits scroll. Here, 10 pixels per second
final = CompositeVideoClip([clip, scrolling_credits, clip.with_mask(mountainmask)])

final.subclip(8, 10).write_videofile("../../credits_mountains.avi")
