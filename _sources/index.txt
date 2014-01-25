MoviePy
=======

MoviePy is a Python module for script-based movie editing, which enables basic operations (cuts, concatenations, title insertions) to be done in a few lines, but can also be used for advanced compositing and special effects. Let me put together the clips in my demonstration folder (you will find the code for most clips in the :ref:`examples`): ::
    
    import os
    from moviepy.editor import *
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
        
You can also do animated GIFs with MoviePy (`examples <http://zulko.github.io/blog/2014/01/23/making-animated-gifs-from-video-files-with-python>`_). 

User's Guide
--------------

.. toctree::
   :maxdepth: 1
   
   install
   crash_course/crash_course
   examples/examples
   ref/ref

How it works, in a nutshell
-----------------------------

MoviePy uses mainly ``ffmpeg`` for reading/writing multimedia files, and Numpy/Scipy for image and sound manipulations.

.. image:: explications.jpeg
    :width: 570px
    :align: center

You can do pretty much any effect you want with MoviePy, but it is just a framework, and in many cases you will need to code a little (or find someone who will !) to come to your goal.




Contribute !
-------------

MoviePy is a (still experimental) open source software written by Zulko_ and released on Github_ and PyPI_ under the MIT licence. Everyone is very welcome to help improve the project, fork it, blog on it, share code for new effects, etc... The more, the merrier !

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

.. _PyPI: https://pypi.python.org/pypi/moviepy
.. _Github: https://github.com/Zulko/moviepy
.. _Zulko: https://github.com/Zulko/
.. _Stackoverflow: http://stackoverflow.com/

