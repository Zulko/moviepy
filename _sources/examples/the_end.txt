======================
"The End" effect
======================

.. raw:: html

        <center>
        <object><param name="movie"
        value="http://www.youtube.com/v/sZMyzzGlsc0&hl=en_US&fs=1&rel=0">
        </param><param name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="http://www.youtube.com/v/sZMyzzGlsc0&hl=en_US&fs=1&rel=0"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="550" height="450"></embed></object>
        </center>
        
So let's explain this one: there is a clip with "The End" written in the middle, and *above* this
clip there is the actual movie. The actual movie has a mask which represents
a white (=opaque) circle on a black (=transparent) background. At the begining,
that circle is so large that you see all the actual movie and you don't see
the "The End" clip. Then the circle becomes progressively smaller and as a
consequence you see less of the actual movie and more of the "The End" clip. ::
    
    from moviepy import *
    from scipy.interpolate import interp1d


    movie = MovieClip("./videos/badl-0006.mov", audio=False)
    clip = movie.subclip(26,31).with_mask()
    w,h = movie.size

    # The mask is a circle with vanishing radius r(t) = 800-200*t
    mask = lambda t: cv2.circle(np.zeros((h,w)),(w/2,h/4),
                      max(0, int(800-200*t)), 1,-1, lineType=cv2.LINE_AA)
                      
    clip.mask.get_frame = mask

    the_end = TextClip("The End",font="Amiri-bold",
               color="white",fontsize=70).set_pos(('center','center'))

    final = CompositeVideoClip(movie.size,[the_end,clip])
    final.duration = clip.duration
    final.to_movie("theEnd.avi")
