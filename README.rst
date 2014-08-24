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
The project is hosted on Github_ , where everyone is welcome to contribute, ask for help or simply give feedback.


Installation
--------------

**Method with pip:** if you have ``pip`` installed, just type this in a terminal (sudo is optional on some systems) ::
    
    (sudo) pip install moviepy

**Method by hand:** download the sources, either on PyPI_ or (if you want the development version) on Github_, unzip everything in one folder, open a terminal and type ::
    
    (sudo) python setup.py install

MoviePy depends on the Python modules Numpy_, Decorator_, and tqdm_, which will be automatically installed during MoviePy's installation.

    
Linking to ffmpeg
~~~~~~~~~~~~~~~~~~

MoviePy requires a **recent version** of the software ffmpeg_ preferably downloaded **directly from the ffmpeg website**.

**Installed ffmpeg:** when you have installed ffmpeg, or (for linux users) when you have a ffmpeg binary in the ``/usr/bin`` folder, it will be detected automatically by MoviePy.

**Non-installed ffmpeg:** you can also simply place the ffmpeg binary somewhere on your computer and specify its path in the file `moviepy.conf`.


Linking to ImageMagick
~~~~~~~~~~~~~~~~~~~~~~~~

ImageMagick_ is not strictly required, but some important features of MoviePy, like the creation of texts or animated GIFs, depend on it.

Once you have installed it, ImageMagick will be automatically detected by MoviePy, **except on Windows !**. Windows user, before installing MoviePy by hand, go into the ``moviepy/`` directory and update the value of ``moviepy.conf`` file and provide the path to the ImageMagick binary called `convert`. It should look like this ::
    
    <imageMagic value="C:\\Program Files\\ImageMagick_VERSION\\convert.exe"/>


Other optional but useful dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PyGame_ is needed for video and sound previews (useless if you intend to work with MoviePy on a server but really essential for advanced video editing *by hand*).

For advanced image processing you will need one or several of these packages. For instance using the method ``clip.resize`` requires that at least one of Scipy, PIL, Pillow or OpenCV are installed.

- The Python Imaging Library (PIL) or, better, its branch Pillow_ .
- Scipy_ (for tracking, segmenting, etc.), and can be used for resizing video clips if PIL and OpenCV aren't installed on your computer.
- `Scikit Image`_ may be needed for some advanced image manipulation.
- `OpenCV 2.4.6`_ (provides the package ``cv2``) or more recent may be needed for some advanced image manipulation.




.. _PyPI: https://pypi.python.org/pypi/moviepy
.. _Pillow: http://pillow.readthedocs.org/en/latest/
.. _Zulko : https://github.com/Zulko
.. _Github: https://github.com/Zulko/moviepy
.. _here: http://zulko.github.io/moviepy/
.. _Scipy: http://www.scipy.org/
.. _`download MoviePy`: https://github.com/Zulko/moviepy
.. _`OpenCV 2.4.6`: http://sourceforge.net/projects/opencvlibrary/files/
.. _Pygame: http://www.pygame.org/download.shtml
.. _Numpy: http://www.scipy.org/install.html
.. _`Scikit Image`: http://scikit-image.org/download.html
.. _Decorator: https://pypi.python.org/pypi/decorator
.. _tqdm: https://github.com/noamraph/tqdm


.. _ffmpeg: http://www.ffmpeg.org/download.html 
.. _ImageMagick: http://www.imagemagick.org/script/index.php
