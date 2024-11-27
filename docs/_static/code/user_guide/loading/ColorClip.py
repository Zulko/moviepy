from moviepy import ColorClip

# Color is passed as a RGB tuple
myclip = ColorClip(size=(200, 100), color=(255, 0, 0), duration=1)
# We really don't need more than 1 fps do we ?
myclip.write_videofile("result.mp4", fps=1)
