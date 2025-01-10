"""Let's position some text and images on a video."""

from moviepy import TextClip, VideoFileClip, CompositeVideoClip, ImageClip

# We load all the clips we want to compose
background = VideoFileClip("example2.mp4").subclipped(0, 2)
title = TextClip(
    "./example.ttf",
    text="Big Buck Bunny",
    font_size=80,
    color="#fff",
    text_align="center",
    duration=1,
)
author = TextClip(
    "./example.ttf",
    text="Blender Foundation",
    font_size=40,
    color="#fff",
    text_align="center",
    duration=1,
)
copyright = TextClip(
    "./example.ttf",
    text="© CC BY 3.0",
    font_size=20,
    color="#fff",
    text_align="center",
    duration=1,
)
logo = ImageClip("./example2.png", duration=1).resized(height=50)

# We want our title to be at the center horizontaly and start at 25%
# of the video verticaly. We can set as "center", "left", "right",
# "top" and "bottom", and % relative from the clip size
title = title.with_position(("center", 0.25), relative=True)

# We want the author to be in the center, 30px under the title
# We can set as pixels
top = background.h * 0.25 + title.h + 30
left = (background.w - author.w) / 2
author = author.with_position((left, top))

# We want the copyright to be 30px before bottom
copyright = copyright.with_position(("center", background.h - copyright.h - 30))

# Finally, we want the logo to be in the center, but to drop as time pass
# We can do so by setting position as a function that take time as argument,
# a lot like frame_function
top = (background.h - logo.h) / 2
logo = logo.with_position(lambda t: ("center", top + t * 30))

# We write the result
final_clip = CompositeVideoClip([background, title, author, copyright, logo])
final_clip.write_videofile("final_clip.mp4")
