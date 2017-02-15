MoviePy
========

MoviePy (full documentation here_) is a Python module for video editing: cuts, concatenations, title insertions, video compositing (a.k.a. non-linear editing), video processing, and creation of custom effects. See the gallery_ for some examples of use.

MoviePy can read and write all the most common audio and video formats, including GIF, and runs on Windows/Mac/Linux, with Python 2.7+ and 3. Here it is in action in an IPython notebook:

.. image:: https://raw.githubusercontent.com/Zulko/moviepy/master/docs/demo_preview.jpeg
    :alt: [logo]
    :align: center

Example
--------

In this example we open a video file, select the subclip between t=50s and t=60s, add a title at the center of the screen, and write the result to a new file: ::

    from moviepy.editor import *

    video = VideoFileClip("myHolidays.mp4").subclip(50,60)

    # Make the text. Many more options are available.
    txt_clip = ( TextClip("My Holidays 2013",fontsize=70,color='white')
                 .set_position('center')
                 .set_duration(10) )

    result = CompositeVideoClip([video, txt_clip]) # Overlay text on video
    result.write_videofile("myHolidays_edited.webm",fps=25) # Many options...



Contribute !
-------------

MoviePy is an open-source software originally written by Zulko_ and released under the MIT licence. The project is hosted on Github_ , where everyone is welcome to contribute, ask for help or simply give feedback.

You can also discuss about the project on Reddit_ or on the mailing list moviepy@librelist.com .


Maintainers
--------------

- Zulko_ - Owner
- mbeacom_


Installation
---------------

MoviePy depends on the Python modules Numpy_, imageio_, Decorator_, and tqdm_, which will be automatically installed during MoviePy's installation. The software FFMPEG should be automatically downloaded/installed (by imageio) during your first use of MoviePy (it takes a few seconds). If you want to use a specific version of FFMPEG, follow the instructions in file ``config_defaults.py``. In case of trouble, provide feedback.

**Installation by hand:** download the sources, either on PyPI_ or (if you want the development version) on Github_, unzip everything in one folder, open a terminal and type ::

    (sudo) python setup.py install

**Installation with pip:** if you have ``pip`` installed, just type this in a terminal: ::

    (sudo) pip install moviepy

If you have neither ``setuptools`` nor ``ez_setup`` installed the command above will fail, is this case type this before installing: ::

    (sudo) pip install ez_setup


Other optional but useful dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ImageMagick_ is not strictly required, only if you want to write texts. It can also be used as a backend for GIFs but you can do GIFs with MoviePy without ImageMagick.

Once you have installed it, ImageMagick will be automatically detected by MoviePy, **except on Windows !**. Windows user, before installing MoviePy by hand, go into the ``moviepy/config_defaults.py`` file and provide the path to the ImageMagick binary called `convert`. It should look like this ::

    IMAGEMAGICK_BINARY = "C:\\Program Files\\ImageMagick_VERSION\\convert.exe"

PyGame_ is needed for video and sound previews (useless if you intend to work with MoviePy on a server but really essential for advanced video editing *by hand*).

For advanced image processing you will need one or several of these packages. For instance using the method ``clip.resize`` requires that at least one of Scipy, PIL, Pillow or OpenCV are installed.

- The Python Imaging Library (PIL) or, better, its branch Pillow_ .
- Scipy_ (for tracking, segmenting, etc.), and can be used for resizing video clips if PIL and OpenCV aren't installed on your computer.
- `Scikit Image`_ may be needed for some advanced image manipulation.
- `OpenCV 2.4.6`_ or more recent (which provides the package ``cv2``) may be needed for some advanced image manipulation.


.. _gallery: http://zulko.github.io/moviepy/gallery.html
.. _Reddit: http://www.reddit.com/r/moviepy/
.. _PyPI: https://pypi.python.org/pypi/moviepy
.. _Pillow: http://pillow.readthedocs.org/en/latest/
.. _Zulko : https://github.com/Zulko
.. _mbeacom : https://github.com/mbeacom
.. _Github: https://github.com/Zulko/moviepy
.. _here: http://zulko.github.io/moviepy/
.. _Scipy: http://www.scipy.org/
.. _`download MoviePy`: https://github.com/Zulko/moviepy
.. _`OpenCV 2.4.6`: http://sourceforge.net/projects/opencvlibrary/files/
.. _Pygame: http://www.pygame.org/download.shtml
.. _Numpy: http://www.scipy.org/install.html
.. _imageio: http://imageio.github.io/
.. _`Scikit Image`: http://scikit-image.org/download.html
.. _Decorator: https://pypi.python.org/pypi/decorator
.. _tqdm: https://github.com/noamraph/tqdm


.. _ffmpeg: http://www.ffmpeg.org/download.html
.. _ImageMagick: http://www.imagemagick.org/script/index.php
