""" requires scikit-image installed (for vfx.painting) """
 
from moviepy.all import *

# WE TAKE THE SUBCLIPS WHICH ARE 2 SECONDS BEFORE & AFTER THE FREEZE

charade = VideoFileClip("../../videos/charade.mp4")
tfreeze = cvsecs(19,21) # Time of the freeze, 19'21

clip_before = charade.coreader().subclip(tfreeze -2,tfreeze)
clip_after = charade.coreader().subclip(tfreeze ,tfreeze +2)


# THE FRAME TO FREEZE

im_freeze = charade.to_ImageClip(tfreeze)
painting = charade.fx( vfx.painting, saturation = 1.6,black = 0.006).\
                   to_ImageClip(tfreeze)
                 
txt = TextClip('Audrey',font='Amiri-regular',fontsize=35)

painting_txt = CompositeVideoClip([painting,txt.set_pos((10,180))]).\
                   add_mask().\
                   set_duration(3).\
                   fx( transfx.crossfadein, 0.5).\
                   fx( transfx.crossfadeout, 0.5)

# FADEIN/FADEOUT EFFECT ON THE PAINTED IMAGE

painting_fading = CompositeVideoClip([im_freeze,painting_txt])

# FINAL CLIP AND RENDERING

final_clip =  concatenate([ clip_before,
                            painting_fading.set_duration(3),
                            clip_after])

final_clip.to_videofile('../../audrey.avi',fps=charade.fps, codec = "mpeg4", audio_bitrate="3000k")
