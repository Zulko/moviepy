from moviepy import *
import os

myclip = VideoFileClip("example.mp4")

# Here we just save in dir output with filename being his index (start at 0, then +1 for each frame)
os.mkdir("./output")
myclip.write_images_sequence("./output/%d.jpg")

# We set the FPS of our GIF at 10, and we leftpad name with 0 up to 4 digits
myclip.write_images_sequence("./output/%04d.jpg")
