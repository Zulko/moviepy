.. _install:

Download and Installation
==========================

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

**Non-installed ffmpeg:** you can also simply place the ffmpeg binary somewhere on your computer and specify its path in the file `moviepy/config_defaults.py` before installing MoviePy by hand.

Linking to ImageMagick
~~~~~~~~~~~~~~~~~~~~~~~~

ImageMagick_ is not strictly required, but some important features of MoviePy, like the creation of texts or animated GIFs, depend on it.

Once you have installed it, ImageMagick will be automatically detected by MoviePy, **except on Windows !**. Windows user, before installing MoviePy by hand, go into the ``moviepy/config_defaults.py`` file and provide the path to the ImageMagick binary called `convert`. It should look like this ::
    
    IMAGEMAGICK_BINARY = "C:\\Program Files\\ImageMagick_VERSION\\convert.exe"


Other optional but useful dependencies
----------------------------------------

PyGame_ is needed for video and sound previews (useless if you intend to work with MoviePy on a server but really essential for advanced video editing *by hand*).

For advanced image processing you will need one or several of these packages. for instance ``clip.resize`` requires that at least one of Scipy, PIL, Pillow or OpenCV are installed.

- The Python Imaging Library (PIL) or, better, its branch Pillow_ .
- Scipy_ (for tracking, segmenting, etc.), and can be used for resizing video clips if PIL and OpenCV aren't installed on your computer.
- `Scikit Image`_ may be needed for some advanced image manipulation.
- `OpenCV 2.4.6`_ (provides the package ``cv2``) or more recent may be needed for some advanced image manipulation. See :ref:`opencv`.

If you are on linux, these softwares will surely be in your repos.    

.. _`Numpy`: http://www.scipy.org/install.html
.. _Decorator: https://pypi.python.org/pypi/decorator
.. _tqdm: https://pypi.python.org/pypi/tqdm

.. _ffmpeg: http://www.ffmpeg.org/download.html 


.. _imageMagick: http://www.imagemagick.org/script/index.php
.. _Pygame: http://www.pygame.org/download.shtml


.. _Pillow: http://pillow.readthedocs.org/en/latest/
.. _Scipy: http://www.scipy.org/
.. _`Scikit Image`: http://scikit-image.org/download.html

.. _Github: https://github.com/Zulko/moviepy
.. _PyPI: https://pypi.python.org/pypi/moviepy
.. _`OpenCV 2.4.6`: http://sourceforge.net/projects/opencvlibrary/files/


