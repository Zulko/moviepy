from moviepy import *

myclip = VideoFileClip("./example.mp4").subclipped(0, 1)  # Keep only 0 to 1 sec

# We preview our clip as a video, inheriting FPS and audio of the original clip
myclip.preview()

# We preview our clip as video, but with a custom FPS for video and audio
# making it less consuming for our computer
myclip.preview(fps=5, audio_fps=11000)

# Now we preview without audio
myclip.preview(audio=False)
