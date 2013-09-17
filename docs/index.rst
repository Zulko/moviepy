MoviePy
=======

MoviePy is a Python module for script-based movie editing, which enables basic operations (cuts, concatenations, title insertions) to be done in a few lines. It can also be used for advanced compositing and special effects. Let me put together the clips in my demonstration folder: ::
    
    import os
    from moviepy.all import *
    files = sorted( os.listdir("clips/") )
    clips = [ VideoFileClip('clips/%s'%f) for f in files]
    video = concatenate(clips, transition = VideoFileClip("logo.avi"))
    video.to_videofile("demos.avi",fps=25, codec="mpeg4")
    
.. raw:: html

        <center>
        <object><param name="movie"
        value="http://www.youtube.com/v/zGhoZ4UBxEQ&hl=en_US&fs=1&rel=0">
        </param><param name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="http://www.youtube.com/v/zGhoZ4UBxEQ&hl=en_US&fs=1&rel=0"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="550" height="450"></embed></object>
        </center>

You will find the code for most clips in the :ref:`examples`.

You can do pretty much any effect you want with MoviePy, but it is just a framework, and in most cases you will need to code a little (or find someone who will !) to come to your goal.


User's Guide
--------------

.. toctree::
   :maxdepth: 1
   
   install
   crash_course/crash_course
   examples/examples
   ref/ref


MoviePy is a (still experimental) open source software written by Zulko_ and released under the MIT licence. Everyone is very welcome to help improve the project, fork it, blog on it, share code for new effects, etc... The more, the merrier !

For troubleshooting and bug reports, the best for now is to ask on Stackoverflow_ (it will advertize for the project :) ) or on the Github project page.

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. raw:: html

        <a href="https://github.com/Zulko/moviepy">
        <img style="position: absolute; top: 0; right: 0; border: 0;"
        src="https://s3.amazonaws.com/github/ribbons/forkme_right_red_aa0000.png"
        alt="Fork me on GitHub"></a>


.. _Zulko: https://github.com/Zulko/
.. _Stackoverflow: http://stackoverflow.com/

