from moviepy import VideoFileClip
from moviepy import vfx, afx

myclip = VideoFileClip("example.mp4")
myclip = myclip.fx(vfx.resize, width=460) # resize clip to be 460px in width, keeping aspect ratio

# fx method return a copy of the clip, so we can easily chain them
myclip = myclip.fx(vfx.multiply_speed, 2).fx(afx.multiply_volume, 0.5) # double the speed and half the audio volume

# because effects are added to Clip at runtime, you can also call them directly from your clip as methods
myclip = myclip.multiply_color(0.5) #dDarken the clip