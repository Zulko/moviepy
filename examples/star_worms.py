"""
Description of the video:
Mimic of Star Wars' opening title. A text with a (false)
perspective effect goes towards the end of space, on a
background made of stars. Slight fading effect on the text.

"""

import numpy as np
from skimage import transform as tf

from moviepy.editor import *
from moviepy.video.tools.drawing import color_gradient


# RESOLUTION

w = 720
h = w*9/16 # 16/9 screen
moviesize = w,h



# THE RAW TEXT
txt = "\n".join([
"A long time ago, in a faraway galaxy,",
"there lived a prince and a princess",
"who had never seen the stars, for they",
"lived deep underground.",
"",
"Many years before, the prince's",
"grandfather had ventured out to the",
"surface and had been burnt to ashes by",
"solar winds.",
"",
"One day, as the princess was coding",
"and the prince was shopping online, a",
"meteor landed just a few megameters",
"from the couple's flat."
])


# Add blanks
txt = 10*"\n" +txt + 10*"\n"


# CREATE THE TEXT IMAGE


clip_txt = TextClip(txt,color='white', align='West',fontsize=25,
                    font='Xolonium-Bold', method='label')


# SCROLL THE TEXT IMAGE BY CROPPING A MOVING AREA

txt_speed = 27
fl = lambda gf,t : gf(t)[int(txt_speed*t):int(txt_speed*t)+h,:]
moving_txt= clip_txt.fl(fl, apply_to=['mask'])


# ADD A VANISHING EFFECT ON THE TEXT WITH A GRADIENT MASK

grad = color_gradient(moving_txt.size,p1=(0,2*h/3),
                p2=(0,h/4),col1=0.0,col2=1.0)
gradmask = ImageClip(grad,ismask=True)
fl = lambda pic : np.minimum(pic,gradmask.img)
moving_txt.mask = moving_txt.mask.fl_image(fl)


# WARP THE TEXT INTO A TRAPEZOID (PERSPECTIVE EFFECT)

def trapzWarp(pic,cx,cy,ismask=False):
    """ Complicated function (will be latex packaged as a fx) """
    Y,X = pic.shape[:2]
    src = np.array([[0,0],[X,0],[X,Y],[0,Y]])
    dst = np.array([[cx*X,cy*Y],[(1-cx)*X,cy*Y],[X,Y],[0,Y]])
    tform = tf.ProjectiveTransform()
    tform.estimate(src,dst)
    im = tf.warp(pic, tform.inverse, output_shape=(Y,X))
    return im if ismask else (im*255).astype('uint8')

fl_im = lambda pic : trapzWarp(pic,0.2,0.3)
fl_mask = lambda pic : trapzWarp(pic,0.2,0.3, ismask=True)
warped_txt= moving_txt.fl_image(fl_im)
warped_txt.mask = warped_txt.mask.fl_image(fl_mask)


# BACKGROUND IMAGE, DARKENED AT 60%

stars = ImageClip('../../videos/stars.jpg')
stars_darkened = stars.fl_image(lambda pic: (0.6*pic).astype('int16'))


# COMPOSE THE MOVIE

final = CompositeVideoClip([
         stars_darkened,
         warped_txt.set_pos(('center','bottom'))],
         size = moviesize)


# WRITE TO A FILE

final.set_duration(8).write_videofile("starworms.avi", fps=5)

# This script is heavy (30s of computations to render 8s of video)



"""=====================================================================

    CODE FOR THE VIDEO TUTORIAL

  We will now code the video tutorial for this video.
  When you think about it, it is a code for a video explaining how to
  make another video using some code (this is so meta !).
  This code uses the variables of the previous code (it should be placed
  after that previous code to work).

====================================================================="""



def annotate(clip,txt,txt_color='white',bg_color=(0,0,255)):
    """ Writes a text at the bottom of the clip. """
    
    txtclip = TextClip(txt, fontsize=20, font='Ubuntu-bold',
                       color=txt_color)
                       
    txtclip = txtclip.on_color((clip.w,txtclip.h+6), color=(0,0,255),
                        pos=(6,'center'))
                        
    cvc =  CompositeVideoClip([clip , txtclip.set_pos((0,'bottom'))])
    
    return cvc.set_duration(clip.duration)


def resizeCenter(clip):
    return clip.resize( height=h).set_pos('center')

    
def composeCenter(clip):
    return CompositeVideoClip([clip.set_pos('center')],size=moviesize)



annotated_clips = [ annotate(clip,text) for clip,text in [
               
(composeCenter(resizeCenter(stars)).subclip(0,3),
    "This is a public domain picture of stars"),

(CompositeVideoClip([stars],moviesize).subclip(0,3),
    "We only keep one part."),

(CompositeVideoClip([stars_darkened],moviesize).subclip(0,3),
    "We darken it a little."),

(composeCenter(resizeCenter(clip_txt)).subclip(0,3),
    "We generate a text image."),

(composeCenter(moving_txt.set_mask(None)).subclip(6,9),
    "We scroll the text by cropping a moving region of it."),

(composeCenter(gradmask.to_RGB()).subclip(0,2),
    "We add this mask to the clip."),

(composeCenter(moving_txt).subclip(6,9),
    "Here is the result"),

(composeCenter(warped_txt).subclip(6,9),
    "We now warp this clip in a trapezoid."),

(final.subclip(6,9),
    "We finally superimpose with the stars.")
]]

# Concatenate and write to a file

concatenate_videoclips(annotated_clips).write_videofile('tutorial.avi', fps=5)