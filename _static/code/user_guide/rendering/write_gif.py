from moviepy import *

myclip = VideoFileClip("example.mp4").subclipped(0, 2)

# Here we just save as GIF
myclip.write_gif("result.gif")

# Here we save as GIF, but we set the FPS of our GIF at 10
myclip.write_gif("result.gif", fps=10)
