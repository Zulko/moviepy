MoviePy
========

MoviePy (full documentation here_) is a Python module for script-based movie editing.

It can read and write to many formats, `including  animated GIFs <http://zulko.github.io/blog/2014/01/23/making-animated-gifs-from-video-files-with-python/>`_, and enables basic operations (cuts, concatenations, title insertions) to be done in a few lines. It can also be used for advanced compositing.

A typical MoviePy script looks like that: ::

    from moviepy.editor import *
    
    # Load myHolidays.mp4 and select the subclip 00:00:50 - 00:00:60
    clip = VideoFileClip("myHolidays.mp4").subclip(50,60)
    
    # Generate a text clip (many options available ! )
    txt_clip = TextClip("My Holidays 2013",fontsize=70,color='white')
    txt_clip = txt_clip.set_pos('center').set_duration(10)
    
    # Overlay the text clip above the first clip
    final_clip = CompositeVideoClip([clip, txt_clip])
    
    # write the result to a file in any format
    final_clip.to_videofile("myHolidays_edited.avi",fps=25, codec='mpeg4')



MoviePy is an open-source software originally written by Zulko_ and released under the MIT licence.
The project is hosted on Github_ , where everyone is welcome to contribute and give feedback.

Download and Installation
---------------------------

MoviePy requires the Python modules Numpy_, Decorator_, and tqdm_. All of these will all be automatically installed during MoviePy's installation.

You will also need a **recent version** of the software ffmpeg_ , preferably downloaded directly from the ffmpeg website.

If you intend to use advanced features you must install a few other dependencies like ImageMagick_ , Pygame_ etc. (see `the docs <http://zulko.github.io/moviepy/install.html>`_).

First installation method : if you have ``pip`` installed, just type this in a terminal (sudo is optional on some systems) ::
    
    (sudo) pip install moviepy

Second method : by hand. Download the sources, either on PyPI_ or (if you want the development version) on Github_, unzip everything in one folder, open a terminal and type ::
    
    (sudo) python setup.py install
    
Linking to ffmpeg
~~~~~~~~~~~~~~~~~~

If you put have a ffmpeg binary in you executable folder (on Linux it will be ``/usr/bin``) it will be detected automatically by MoviePy. Else make sure that MoviePy can locate ffmpeg on your computer by running the script ``moviepy/conf.py`` that is in the sources. It it fails, then you must enter the path to the FFMPEG executable in the first line of this file ::
    
    FFMPEG_BINARY = path/to/your/ffmpeg



.. _PYPI: https://pypi.python.org/pypi/moviepy
.. _Zulko : https://github.com/Zulko
.. _Github: https://github.com/Zulko/moviepy
.. _here: http://zulko.github.io/moviepy/
.. _`download MoviePy`: https://github.com/Zulko/moviepy
.. _`OpenCV 2.4.6`: http://sourceforge.net/projects/opencvlibrary/files/
.. _Pygame: http://www.pygame.org/download.shtml
.. _`Numpy`: http://www.scipy.org/install.html
.. _`Scikit Image`: http://scikit-image.org/download.html
.. _Decorator: https://pypi.python.org/pypi/decorator
.. _tqdm: https://github.com/noamraph/tqdm


.. _ffmpeg: http://www.ffmpeg.org/download.html 
.. _ImageMagick: http://www.imagemagick.org/script/index.php
