MoviePy
=======

MoviePy is a Python module for script-based movie editing. It enables basic operations (cuts, concatenations, title insertions) to be done in a few lines, and can be used for advanced compositing and special effects.

It can read and write to many formats, `including animated GIFs <http://zulko.github.io/blog/2014/01/23/making-animated-gifs-from-video-files-with-python>`_.

Let us put together a few demonstration clips (you will find the code for most of these in the :ref:`examples`): ::
    
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
        allowfullscreen="true" width="490" height="390"></embed></object>
        </center>

MoviePy is an open source software originally written by Zulko_ and released under the MIT licence.
It is hosted on Github_, where you can push improvements, report bugs and ask for help.

**Very New:** there is now a MoviePy forum on Reddit_ and a mailing list on librelist_ .

.. raw:: html

    <a href="https://twitter.com/share" class="twitter-share-button"
    data-text="MoviePy, script-based video editing" data-size="large" data-hashtags="MoviePy">Tweet
    </a>
    <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';
    if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';
    fjs.parentNode.insertBefore(js,fjs);}}(document, 'script', 'twitter-wjs');
    </script>
    
    <iframe src="http://ghbtns.com/github-btn.html?user=Zulko&repo=moviepy&type=watch&count=true&size=large"
    allowtransparency="true" frameborder="0" scrolling="0" width="152px" height="30px"></iframe>
    
    <a href="https://github.com/Zulko/moviepy">
    <img style="position: absolute; top: 0; right: 0; border: 0;"
    src="https://s3.amazonaws.com/github/ribbons/forkme_right_red_aa0000.png"
    alt="Fork me on GitHub"></a>


User's Guide
--------------

.. toctree::
   :maxdepth: 1
   
   install
   crash_course/crash_course
   examples/examples
   FAQ
   ref/ref


.. _PyPI: https://pypi.python.org/pypi/moviepy
.. _Zulko: https://github.com/Zulko/
.. _Stackoverflow: http://stackoverflow.com/
.. _Github: https://github.com/Zulko/moviepy
.. _Reddit: http://www.reddit.com/r/moviepy/
.. _librelist: mailto:moviepy@librelist.com
