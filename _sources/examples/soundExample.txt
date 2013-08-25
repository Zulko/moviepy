.. soundexample:

An example with sound
------------------------

An example of using MoviePy to assemble movie clips with sounds. Here are two scenes of Charade put together:

.. raw:: html

        <center>
        <object><param name="movie"
        value="http://www.youtube.com/v/gtyFuIoH7W0&hl=en_US&fs=1&rel=0">
        </param><param name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="http://www.youtube.com/v/gtyFuIoH7W0&hl=en_US&fs=1&rel=0"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="550" height="450"></embed></object>
        </center>

Here is the code: ::
    
    from moviepy import *
    import numpy as np
    
    # LOAD MOVIE

    charade = MovieClip("./charadePhone.mp4",audio=True)
    w,h = charade.size
    duration=6



    # MAKE THE LEFT CLIP

    # cut and crop the clip
    xleft = 60
    clip_left = charade.subclip(0,duration)
    clip_left = clip_left.crop(x1=xleft,x2=xleft+2*w/3)

    # make the mask. Yeah it's complicated, there must be a simpler way.
    # It is just a mask that is black on the right bottom corner.
    c1a = np.array((2*w/3,0))
    v1 = np.array([h,w/3])
    v1 = 2*v1/np.linalg.norm(v1)
    c1b = c1a- v1
    g1 = gradient(clip_left.size,c1a,c1b,col1=0,col2=1.0)
    clip_left.mask = ImageClip(g1,ismask=True)             



    # MAKE THE RIGHT CLIP

    # cut and crop the clip
    xright = 70
    clip_right = charade.subclip(21,21+duration)
    clip_right = clip_right.crop(x1=xright,x2=xright+2*w/3)

    # make the mask
    c2a = np.array((w/3,0))
    c2b = c2a+v1
    g2 = gradient(clip_right.size,c2a,c2b,col1=0,col2=1.0)
    clip_right.mask = ImageClip(g2,ismask=True)
    
    
    # ASSEMBLE AND WRITE THE MOVIE

    cc = CompositeVideoClip(charade.size,
                [clip_right.set_pos(('right',0)),
                 clip_left.set_pos(('left',0))])

    cc.to_movie("biphone.avi")

 
A few remarks:

- In this script we never explicitly consider the sound. MoviePy does all the cutting and the mixing automatically.
- We do not load the whole movie but just a part of it (never load a 2h00 movie when you are going to use its sound, see the remark in :ref:`goodPractices`). Rather, we first extract the part of interest with ::
      
      import moviepy.ffmpeg as ff
      t1 = 3050 #seconds
      t2 = 3095
      ff.extract_subclip("charade.mp4",t1,t2,"charadePhone.mp4")
      
- We use a nerdy and complicated way of cutting the clips with the ``gradient`` function (defined in :ref:`gradients`) but you could have done it with masks from images for instance.


