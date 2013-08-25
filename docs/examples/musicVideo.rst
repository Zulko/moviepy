======================
A simple music video
======================

.. raw:: html

        <center>
        <object><param name="movie"
        value="http://www.youtube.com/v/AqGZ4JFkQTU&hl=en_US&fs=1&rel=0">
        </param><param name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="http://www.youtube.com/v/AqGZ4JFkQTU&hl=en_US&fs=1&rel=0"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="550" height="450"></embed></object>
        </center>


This is an example, with no sound (lame for a music video), soon to be
replaced with a real music video example (the code will be 99% the same).
The philosophy of MoviePy is that for each new music video I will make,
I will just have to copy/paste this code, and modify a few lines. ::
    
    from moviepy import *


    # UKULELE CLIP, OBTAINED BY CUTTING AND CROPPING
    # RAW FOOTAGE

    ukulele = (MovieClip("./videos/moi_ukulele.MOV",audio=False).
                   subclip(60+33,60+50).
                   crop(486,180,1196,570))

    w,h = moviesize = ukulele.size

    # THE PIANO FOOTAGE IS DOWNSIZED, HAS A WHITE MARGIN, IS
    # IN THE BOTTOM LEFT CORNER 

    piano = (MovieClip("./videos/douceamb.mp4",audio=False).
                 subclip(30,50).
                 resize((w/3,h/3)).
                 margin(6,color=(255,255,255)). #white margin
                 margin(bottom=20,right=20, opacity=0). # transparent
                 set_pos(('right','bottom')) )


    # A CLIP WITH A TEXT AND A BLACK SEMI-OPAQUE BACKGROUND


    txt = TextClip("V. Zulkoninov - Ukulele Sonata",
                       color='white',fontsize=24)
    txt_col = txt.on_color(size=(ukulele.w + txt.w,txt.h+6), color=(0,0,0),
                       pos=(6,'center'), col_opacity=0.6)

    # THE TEXT CLIP IS ANIMATED.
    # I am *NOT* explaining the formula, understands who can/want.
    txt_mov = txt_col.set_pos( lambda t: (max(w/30,int(w-0.5*w*t)),
                                      max(5*h/6,int(100*t))) )

    # FINAL ASSEMBLY
    final = CompositeVideoClip(moviesize,[ukulele,txt_mov,piano])
    final.subclip(0,5).to_movie("ukulele.avi",fps=24,codec='DIVX')
