.. _mountainMask:

Partially Hidden credits
-----------------------------------

.. raw:: html

        <center>
        <object><param name="movie"
        value="http://www.youtube.com/v/NsTgBah6Ebk&hl=en_US&fs=1&rel=0">
        </param><param name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="http://www.youtube.com/v/NsTgBah6Ebk&hl=en_US&fs=1&rel=0"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="550" height="450"></embed></object>
        </center>

First, see in :ref:`autocredits` how to make credits automatically with MoviePy. Before seeing the code for this video, here is a tutorial video that explains the different steps (also made with MoviePy):
 
.. raw:: html

        <center>
        <object><param name="movie"
        value="http://www.youtube.com/v/7tKABfc0Yzw&hl=en_US&fs=1&rel=0">
        </param><param name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="http://www.youtube.com/v/7tKABfc0Yzw&hl=en_US&fs=1&rel=0"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="550" height="450"></embed></object>
        </center>





And here is the code: ::
    
    from moviepy import *
    
    # Load the mountains clip, cut it, slow it down, make it look darker
    clip = MovieClip('./mountain.mov',audio=False).subclip(37,46).speedx(0.4)
    clip = clip.fl_image(lambda pic: (0.7*pic).astype('uint8'))
    
    # Save the first frame to later make a mask with GIMP (only once)
    # clip.save_frame('mountain.png')
    
    # Load the mountain mask made with GIMP
    mountainmask = ImageClip('./credits/mountainMask2.png',ismask=True)
    
    # Generate the credits from a text file
    credits = make_credits('./credits/credits.txt',3*clip.w/4)
    
    # Make the credits scroll. Here, 10 pixels per second
    mov_credits= CompositeVideoClip(clip.size,[
                    clip,
                    credits.set_pos(lambda t:('center',-10*t)),
                    clip.set_mask(mountainmask)])

    final = CompositeVideoClip(clip.size,[clip,mov_credits.set_end(25)])
    final.subclip(8,15).to_movie("credits_mount.avi",fps=24,codec='DIVX')
