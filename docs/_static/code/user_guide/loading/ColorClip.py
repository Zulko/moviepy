from moviepy import *

myclip = ColorClip(
    size=(200, 100), color=(255, 0, 0), duration=1
)  # Color is passed as a RGB tuple
myclip.write_videofile(
    "result.mp4", fps=1
)  # We really dont need more than 1 fps do we ?
