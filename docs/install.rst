.. _install:

Download and Installation
==========================


Installation
--------------

**Method with pip:** if you have ``pip`` installed, just type this in a terminal

.. code:: bash

    $ (sudo) pip install moviepy

**Method by hand:** Download the sources, either on PyPI_ or (if you want the development version) on Github_, unzip everything in one folder, open a terminal and type

.. code:: bash

    $ (sudo) python setup.py install

MoviePy depends on the Python modules NumPy_, Imageio_, Decorator_, and Proglog_, which will be automatically installed during MoviePy's installation.

MoviePy depends on the software FFmpeg for video reading and writing. You don't need to worry about that, as FFmpeg should be automatically downloaded/installed by ImageIO during your first use of MoviePy (it takes a few seconds). If you want to use a specific version of FFmpeg, you can set the
`FFMPEG_BINARY` environment variable.


Other optional but useful dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can install ``moviepy`` with all dependencies via:

.. code:: bash

    $ (sudo) pip install moviepy[optional]


ImageMagick_ is not strictly required, but needed if you want to use TextClips_. It can also be used as a backend for GIFs, though you can also create GIFs with MoviePy without ImageMagick.

Once you have installed ImageMagick, MoviePy will try to autodetect the path to its executable. If it fails, you can still configure it by setting environment variables (see below).

PyGame_ is needed for video and sound previews (useless if you intend to work with MoviePy on a server but really essential for advanced video editing *by hand*).

For advanced image processing you will need one or several of the following packages. For instance using the method ``clip.resize`` requires that at least one of Scipy, PIL, Pillow or OpenCV are installed.

- Pillow_, the Python Imaging Library, .
- Scipy_ is needed for tracking, segmenting, etc., and can be used for resizing video clips if PIL and OpenCV aren't installed on your computer.
- `Scikit Image`_ may be needed for some advanced image manipulation.
- `OpenCV`_ (provides the package ``cv2``) may be needed for some advanced image manipulation.

If you are on Linux, these packages will likely be in your repos.

For Ubuntu 16.04LTS users, after installing MoviePy, ImageMagick may not be detected by MoviePy. This bug can be fixed by modifying the file ``/etc/ImageMagick-6/policy.xml`` commenting out the statement::

    <!-- <policy domain="path" rights="none" pattern="@*" /> -->


Custom paths to external tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are a couple of environment variables used by MoviePy that allow you
to configure custom paths to the external tools.

To setup any of these variables, the easiest way is to do it in Python before importing objects from MoviePy. For example:

.. code-block:: python

    import os
    os.environ["FFMPEG_BINARY"] = "/path/to/custom/ffmpeg"


Alternatively, after installing the optional dependencies, you can create
a ``.env`` file in your working directory that will be automatically read.
For example

.. code-block:: ini

    FFMPEG_BINARY=/path/to/custom/ffmpeg


There are 2 available environment variables:

``FFMPEG_BINARY``
    Normally you can leave it to its default ('ffmpeg-imageio') in which
    case imageio will download the right ffmpeg binary (on first use) and then always use that binary.

    The second option is ``"auto-detect"``. In this case ffmpeg will be whatever
    binary is found on the computer: generally ``ffmpeg`` (on Linux/macOS) or ``ffmpeg.exe`` (on Windows).

    Lastly, you can set it to use a binary at a specific location on your disk by specifying the exact path.


``IMAGEMAGICK_BINARY``
    The default is ``"auto-detect"``.

    You can set it to use a binary at a specific location on your disk. On Windows, this might look like::

        os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-6.8.8-Q16\magick.exe"

    Note: If you are using a legacy version of ImageMagick, the executable could be ``convert.exe`` instead.


To test if FFmpeg and ImageMagick are found by MoviePy, in a Python console run:

.. code-block:: python

    >>> from moviepy.config import check
    >>> check()

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
.. _`OpenCV`: https://github.com/skvark/opencv-python

.. _Github: https://github.com/Zulko/moviepy
.. _PyPI: https://pypi.python.org/pypi/moviepy


