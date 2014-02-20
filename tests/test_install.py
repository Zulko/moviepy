

from moviepy.editor import *

W,H = (150,180)
color_clips_props =  [{ 'color':[0,0,255],
                        'init_pos':[]
[0,0,255],[0,255,0],[255,0,0]
red_clip, green_clip, blue_clip = [ColorClip((W,H),color=c)
                                   for c in RED, GREEN, BLUE]
