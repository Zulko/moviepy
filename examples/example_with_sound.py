"""
Description of the video:
The screen is split in two parts showing Carry and Audrey at the phone,
talking at the same time, because it is actually two scenes of a same
movie put together.
"""

from moviepy.all import *
from moviepy.video.tools.drawing import color_split


duration = 6 # duration of the final clip

# LOAD THE MAIN SCENE
# this small video contains the two scenes that we will put together.

main_clip = VideoFileClip("../../charadePhone.mp4")
W,H = main_clip.size



# MAKE THE LEFT CLIP : cut, crop, add a mask 

clip_left = main_clip.coreader().subclip(0,duration).\
                fx( vfx.crop, x1=60, x2=60 + 2*W/3)
                            
mask = color_split((2*W/3,H), p1=(W/3,H), p2=(2*W/3,0),
                   col1=1, col2=0, grad_width=2)
                   
clip_left.mask = ImageClip(mask, ismask=True)


# MAKE THE RIGHT CLIP : cut, crop, add a mask 

clip_right = main_clip.coreader().subclip(21,21+duration).\
                   fx( vfx.crop, x1=70, x2=70+2*W/3)
                   
mask = color_split((2*W/3,H), p1=(2,H), p2=(W/3+2,0),
                   col1=0, col2=1, grad_width=2)
                   
clip_right.mask = ImageClip(mask, ismask=True)



# ASSEMBLE AND WRITE THE MOVIE TO A FILE

cc = CompositeVideoClip([clip_right.set_pos('right').fx(afx.volumex, 0.4),
                         clip_left.set_pos('left').fx(afx.volumex, 0.4)],
                         size = (W,H))
#cc.preview()
cc.to_videofile("../../biphone3.avi",fps=24, codec='mpeg4')
