A Star-Wars like opening title
-------------------------------

This is an approximate effect (the perspective would require some more complex transformations) but it is a nice exercice. Achtung: clip with sound.

.. raw:: html

        <center>
        <object><param name="movie"
        value="http://www.youtube.com/v/5euLdo8L0o0&hl=en_US&fs=1&rel=0">
        </param><param name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="http://www.youtube.com/v/5euLdo8L0o0&hl=en_US&fs=1&rel=0"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="550" height="450"></embed></object>
        </center>

Before seeing the code, let us have a look at this tutorial which shows the different steps:

.. raw:: html

        <center>
        <object><param name="movie"
        value="http://www.youtube.com/v/dGrP7GhzWEE&hl=en_US&fs=1&rel=0">
        </param><param name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="http://www.youtube.com/v/dGrP7GhzWEE&hl=en_US&fs=1&rel=0"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="550" height="450"></embed></object>
        </center>
        
And here you are for the code (it uses the ``gradient`` function, see :ref:`gradients`): ::
    
    from moviepy import *
    from skimage import transform as tf
    
    def trapzWarp(pic,cx,cy,ismask=False):
        """" Warps the given picture into a trapezoid.
             Warning: slow function. """
        Y,X = pic.shape[:2]
        src = np.array([[0,0],[X,0],[X,Y],[0,Y]])
        dst = np.array([[cx*X,cy*Y],[(1-cx)*X,cy*Y],[X,Y],[0,Y]])
        tform = tf.ProjectiveTransform()
        tform.estimate(src,dst)
        im = tf.warp(pic, tform.inverse, output_shape=(Y,X))
        return im if ismask else (im*255).astype('uint8')

    # RESOLUTION 16 / 9
    w = 720
    h = w*9/16
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


    clip_txt = TextClip(txt,color='white',
                    align='West',fontsize=25,font='Xolonium-Bold',
                    method='label',remove_temp=False)



    # SCROLL THE TEXT IMAGE BY CROPPING A MOVING AREA

    txt_speed = 27
    fl = lambda gf,t : gf(t)[int(txt_speed*t):int(txt_speed*t)+h,:]
    moving_txt= clip_txt.fl(fl, applyto=['mask'])


    # ADD VANISHING EFFECT ON THE TEXT

    grad = gradient(moving_txt.size,c1=(0,2*h/3),
                    c2=(0,h/4),col1=1.0,col2=0.0)
    gradmask = ImageClip(grad,ismask=True)
    fl = lambda pic : np.minimum(pic,gradmask.img)
    moving_txt.mask = moving_txt.mask.fl_image(fl)


    # WARP THE TEXT (PERSPECTIVE EFFECT)

    fl_im = lambda pic : trapzWarp(pic,0.2,0.3)
    fl_mask = lambda pic : trapzWarp(pic,0.2,0.3, ismask=True)
    warped_txt= moving_txt.fl_image(fl_im)
    warped_txt.mask = warped_txt.mask.fl_image(fl_mask)


    # BACKGROUND IMAGE, DARKENED AT 60%

    stars = ImageClip('./starworms/stars.jpg')
    stars_darkened = stars.fl_image(lambda pic: (0.6*pic).astype('int16'))


    # COMPOSE THE MOVIE


    txt_duration = 2*clip_txt.size[1]/txt_speed
    movie_duration = txt_duration+5

    cc = CompositeVideoClip(moviesize,[
             stars.set_duration(movie_duration),
             warped_txt.set_duration(txt_duration)
                      .set_pos(('center','bottom'))])


    cc.subclip(0,3).preview()


Code for the tutorial
~~~~~~~~~~~~~~~~~~~~~~

Here is the code I used to make the tutorial. When you think about it, it is a code for a video explaining how to make another video using some code (this is so meta !). This code uses the variables of the previous code (it should be placed after that previous code to work). Once again, scripting is very useful to make such videos. ::
    
    def annotate(clip,txt,txt_color='white',bg_color=(0,0,255)):
        """ Writes a text at the bottom of the clip. """
        
        txtclip = TextClip(txt, fontsize=20, font='Ubuntu-bold',
                           color=txt_color)
        
        cvc =  CompositeVideoClip(clip.size,
                [clip , txtclip.on_color((clip.w,txtclip.h+6),
                                color=(0,0,255),pos=(6,'center')).
                                set_pos((0,'bottom'))])
        
        return cvc.set_duration(clip.duration)

    # A few functions to resize/center clips that have different sizes.
    
    def resizeCenter(clip):
        return clip.resize(height=h).set_pos(('center','center'))

    def composeCenter(clip):
        return CompositeVideoClip(moviesize,
                    [clip.set_pos(('center','center'))])
    
    # Annotations
    
    annotations = [
                   
    annotate(composeCenter(resizeCenter(stars)).subclip(0,3),
             "This is a public domain picture of stars"),

    annotate(CompositeVideoClip(moviesize,[stars]).subclip(0,3),
             "We only keep one part."),

    annotate(CompositeVideoClip(moviesize,[stars_darkened]).subclip(0,3),
             "We darken it a little."),

    annotate(composeCenter(resizeCenter(clip_txt)).subclip(0,3),
             "We generate a text image."),

    annotate(composeCenter(moving_txt.set_mask(None)).subclip(6,9),
             "We scroll the text by cropping a moving region of it."),

    annotate(composeCenter(gradmask.toRGB()).subclip(0,2),
             "We add this mask to the clip."),

    annotate(composeCenter(moving_txt).subclip(6,9),
             "Here is the result"),

    annotate(composeCenter(warped_txt).subclip(6,9),
             "We now warp this clip in a trapezoid."),

    annotate(cc.subclip(6,9),
             "We finally superimpose with the stars.")
    ]

    annotations_video = concat(annotations)
    annotations_video.to_movie('tutorial.avi')
