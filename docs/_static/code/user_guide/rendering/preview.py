from moviepy import *

myclip = VideoFileClip('./example.mp4')

# We preview our clip as a video, inheriting FPS and audio of the original clip
myclip.preview()

# We preview our clip as video, but with a custom FPS for video and audio
# making it less consuming for our computer
myclip.preview(fps=10, audio_fps=11000)

# Now we preview our clip to show only portion from 00:00:30 to 00:00:35
myclip.with_subclip(30, 35).preview(fps=10, audio=False)
