.. _install:

Download and Installation
==========================


Installation
--------------

**Method with pip:** if you have ``pip`` installed, just type this in a terminal (it will install ez_setup if you don't already have it) ::

    (sudo) pip install moviepy

If you have neither ``setuptools`` nor ``ez_setup`` installed the command above will fail, is this case type this before installing: ::

    (sudo) pip install ez_setup

**Method by hand:** download the sources, either on PyPI_ or (if you want the development version) on Github_, unzip everything in one folder, open a terminal and type ::

    (sudo) python setup.py install

MoviePy depends on the Python modules Numpy_, imageio_, Decorator_, and tqdm_, which will be automatically installed during MoviePy's installation. It should work  on Windows/Mac/Linux, with Python 2.7+ and 3 ; if you have trouble installing MoviePy or one of its dependencies, please provide feedback !

MoviePy depends on the software FFMPEG for video reading and writing. You don't need to worry about that, as FFMPEG should be automatically downloaded/installed by ImageIO during your first use of MoviePy (it takes a few seconds). If you want to use a specific version of FFMPEG, you can set the FFMPEG_BINARY environment variable See ``moviepy/config_defaults.py`` for details.


Other optional but useful dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ImageMagick_ is not strictly required, only if you want to write texts. It can also be used as a backend for GIFs but you can do GIFs with MoviePy without ImageMagick.

Once you have installed it, ImageMagick will be automatically detected by MoviePy, **except on Windows !**. Windows user, before installing MoviePy by hand, go into the ``moviepy/config_defaults.py`` file and provide the path to the ImageMagick binary called `magick`. It should look like this ::

    IMAGEMAGICK_BINARY = "C:\\Program Files\\ImageMagick_VERSION\\magick.exe"

You can also set the IMAGEMAGICK_BINARY environment variable See ``moviepy/config_defaults.py`` for details.

If you are using an older version of ImageMagick, keep in mind the name of the executable is not ``magick.exe`` but ``convert.exe``. In that case, the IMAGEMAGICK_BINARY property should be ``C:\\Program Files\\ImageMagick_VERSION\\convert.exe``

PyGame_ is needed for video and sound previews (useless if you intend to work with MoviePy on a server but really essential for advanced video editing *by hand*).

For advanced image processing you will need one or several of these packages. For instance using the method ``clip.resize`` requires that at least one of Scipy, PIL, Pillow or OpenCV are installed.

- The Python Imaging Library (PIL) or, better, its branch Pillow_ .
- Scipy_ (for tracking, segmenting, etc.), and can be used for resizing video clips if PIL and OpenCV aren't installed on your computer.
- `Scikit Image`_ may be needed for some advanced image manipulation.
- `OpenCV 2.4.6`_ or more recent (provides the package ``cv2``) or more recent may be needed for some advanced image manipulation.

If you are on linux, these packages will likely be in your repos.

.. _`Numpy`: https://www.scipy.org/install.html
.. _Decorator: https://pypi.python.org/pypi/decorator
.. _tqdm: https://pypi.python.org/pypi/tqdm

.. _ffmpeg: https://www.ffmpeg.org/download.html


.. _imageMagick: https://www.imagemagick.org/script/index.php
.. _Pygame: https://www.pygame.org/download.shtml
.. _imageio: https://imageio.github.io/

.. _Pillow: https://pillow.readthedocs.org/en/latest/
.. _Scipy: https://www.scipy.org/
.. _`Scikit Image`: http://scikit-image.org/download.html

.. _Github: https://github.com/Zulko/moviepy
.. _PyPI: https://pypi.python.org/pypi/moviepy
.. _`OpenCV 2.4.6`: https://sourceforge.net/projects/opencvlibrary/files/


