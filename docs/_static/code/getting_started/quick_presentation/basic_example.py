# Import everything needed to edit video clips
from moviepy import *

# Load example.mp4 and extract only the subclip from 00:00:50 to 00:00:60
clip = VideoFileClip("example.mp4").subclip(50, 60)

# Reduce the audio volume to 80% of his original volume
clip = clip.multiply_volume(0.8)

# Generate a text clip. You can customize the font, color, etc.
txt_clip = TextClip("My Holidays 2013", fontsize=70, color='white')

# Say that you want it to appear for 10s at the center of the screen
txt_clip = txt_clip.with_position('center').with_duration(10)

# Overlay the text clip on the first video clip
video = CompositeVideoClip([clip, txt_clip])

# Write the result to a file (many options available!)
video.write_videofile("result.webm")
