.. _install:

Download and Installation
==========================


Installation
--------------

**Method with pip:** if you have ``pip`` installed, just type this in a terminal (it will install ez_setup if you don't already have it)

.. code:: bash

    $ (sudo) pip install moviepy

If you have neither ``setuptools`` nor ``ez_setup`` installed the command above will fail. In this case type this before installing:

.. code:: bash

    $ (sudo) pip install setuptools

**Method by hand:** download the sources, either on PyPI_ or (if you want the development version) on Github_, unzip everything in one folder, open a terminal and type

.. code:: bash

    $ (sudo) python setup.py install

MoviePy depends on the Python modules NumPy_, Imageio_, Decorator_, and Proglog_, which will be automatically installed during MoviePy's installation. It should work  on Windows/Mac/Linux, with Python 2.7+ and 3 ; if you have trouble installing MoviePy or one of its dependencies, please provide feedback !

MoviePy depends on the software FFMPEG for video reading and writing. You don't need to worry about that, as FFMPEG should be automatically downloaded/installed by ImageIO during your first use of MoviePy (it takes a few seconds). If you want to use a specific version of FFMPEG, you can set the '
`FFMPEG_BINARY` environment variable.


Other optional but useful dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can install ``moviepy`` with all dependencies via:

.. code:: bash

    $ (sudo) pip install moviepy[optional]


ImageMagick_ is not strictly required, but needed if you want to use TextClips_. It can also be used as a backend for GIFs, though you can also create GIFs with MoviePy without ImageMagick.

Once you have installed ImageMagick, MoviePy will try to autodetect the path to its executable. If it fails, you can still configure it by setting environment variables.

PyGame_ is needed for video and sound previews (useless you intend to work with MoviePy on a server but really essential for advanced video editing *by hand*).

For advanced image processing you will need one or several of these packages. For instance using the method ``clip.resize`` requires that at least one of Scipy, PIL, Pillow or OpenCV are installed.

- The Python Imaging Library (PIL) or, better, its branch Pillow_ .
- Scipy_ (for tracking, segmenting, etc.), and can be used for resizing video clips if PIL and OpenCV aren't installed on your computer.
- `Scikit Image`_ may be needed for some advanced image manipulation.
- `OpenCV 2.4.6`_ or more recent (provides the package ``cv2``) or more recent may be needed for some advanced image manipulation.

If you are on Linux, these packages will likely be in your repos.


Custom paths to external tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are a couple of environment variables used by MoviePy that allow you
to configure custom paths to the external tools. 

To setup any of these variables, the easiest way is to do it in Python before
importing objects from MoviePy. For example:

.. code-block:: python

    import os
    os.environ["FFMPEG_BINARY"] = "my/custom/ffmpeg"

    from moviepy.editor import VideoFileClip

Alternatively, after installing the optional dependencies, you can create
a ``.env`` file in your working directory that will be automatically read.

There are 2 available environment variables:

``FFMPEG_BINARY``
    Normally you can leave this one to its default ('ffmpeg-imageio') in which
    case imageio will download the right ffmpeg binary (on first use) and then always use that binary.

    The second option is ``auto-detect``. In this case ffmpeg will be whatever
    binary is found on the computer: generally ``ffmpeg`` (on Linux/macOS) or ``ffmpeg.exe`` (on Windows).

    Lastly, if you want to use a binary at a special location on your disk, enter it like this::

        FFMPEG_BINARY = r"path/to/ffmpeg" # on linux
        FFMPEG_BINARY = r"path\to\ffmpeg.exe" # on windows

    Warning: the 'r' before the path is important, especially on Windows.


``IMAGEMAGICK_BINARY``
    The default is `auto-detect`.
    For Linux users, `convert` should be fine.
    For Windows users, you must specify the path to the ImageMagick
    'magick' binary. For instance::

        IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-6.8.8-Q16\magick.exe"

    Note: If you are using a legacy version of ImageMagick, the executable could be ``convert.exe`` instead.


.. _`Numpy`: https://www.scipy.org/install.html
.. _decorator: https://pypi.python.org/pypi/decorator
.. _proglog: https://pypi.org/project/proglog/

.. _ffmpeg: https://www.ffmpeg.org/download.html

.. _TextClips: https://zulko.github.io/moviepy/ref/VideoClip/VideoClip.html#textclip

.. _imageMagick: https://www.imagemagick.org/script/index.php
.. _Pygame: https://www.pygame.org/download.shtml
.. _imageio: https://imageio.github.io/

.. _Pillow: https://pillow.readthedocs.org/en/latest/
.. _Scipy: https://www.scipy.org/
.. _`Scikit Image`: http://scikit-image.org/download.html

.. _Github: https://github.com/Zulko/moviepy
.. _PyPI: https://pypi.python.org/pypi/moviepy
.. _`OpenCV 2.4.6`: https://sourceforge.net/projects/opencvlibrary/files/


