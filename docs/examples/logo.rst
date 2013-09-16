=================================
MoviePy logo with a moving shadow
=================================
.. raw:: html

        <center>
        <object><param name="movie"
        value="http://www.youtube.com/v/TG86KzL18NA&hl=en_US&fs=1&rel=0">
        </param><param name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="http://www.youtube.com/v/TG86KzL18NA&hl=en_US&fs=1&rel=0"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="550" height="450"></embed></object>
        </center>

Here the logo is a picture, while the shadow is actually a black rectangle taking the whole screen, overlaid over the logo, but with a moving mask composed of a bi-gradient, such that only one (moving) part of the rectangle is visible. See :ref:`gradients` for the code of the function `biGradient`: ::
    
    def f(t,size,duration, a = np.pi/3, thickness = 20):
        w,h = size
        v = thickness* np.array([np.cos(a),np.sin(a)])[::-1]
        center = [int(t*w/duration),h/2]
        return biGradientScreen(size,center,v,0.6,0.0)

    w,h = moviesize = (720,380)
    im = ImageClip("./logo_descr.png", transparent=True)
    im = im.resize(width=w/2)

    duration = 1
    shade = ColorClip(moviesize,col=(0,0,0)).with_mask()
    shade.mask.get_frame = lambda t : f(t,moviesize,duration)
    cc = CompositeVideoClip(moviesize,[im.set_pos(2*["center"]),shade])

    cc.subclip(0,duration).to_videofile("moviepy_logo.avi",fps=24)
