from moviepy import *

# We load all the clips we want to compose
background = VideoFileClip("long_examples/example2.mp4").subclipped(0, 10)
title = TextClip(
    "./example.ttf",
    text="Big Buck Bunny",
    font_size=80,
    color="#fff",
    text_align="center",
    duration=3,
).with_position(("center", "center"))

# We make our final clip through composition
final_clip = CompositeVideoClip([background, title])

# And finally we can write the result into a file

# Here we just save as MP4, inheriting FPS, etc. from final_clip
final_clip.write_videofile("result.mp4")

# Here we save as MP4, but we set the FPS of the clip to our own, here 24 fps, like cinema
final_clip.write_videofile("result24fps.mp4", fps=24)

# Now we save as WEBM instead, and we want tu use codec libvpx-vp9 (usefull when mp4 + transparency).
# We also want ffmpeg compression optimisation as minimal as possible. This will not change
# the video quality and it will decrease time for encoding, but increase final file size a lot.
# Finally, we want ffmpeg to use 4 threads for video encoding. You should probably leave that
# to default, as ffmpeg is already quite good at using the best setting on his own.
final_clip.write_videofile(
    "result.webm", codec="libvpx-vp9", fps=24, preset="ultrafast", threads=4
)
