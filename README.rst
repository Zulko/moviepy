MoviePy
=======

.. image:: https://badge.fury.io/py/moviepy.svg
    :target: PyPI_
    :alt: MoviePy page on the Python Package Index
.. image:: https://badges.gitter.im/movie-py/gitter.png
    :target: Gitter_
    :alt: Discuss MoviePy on Gitter
.. image:: https://travis-ci.org/Zulko/moviepy.svg?branch=master
    :target: https://travis-ci.org/Zulko/moviepy
    :alt: Build status on travis-ci
.. image:: https://ci.appveyor.com/api/projects/status/github/zulko/moviepy?svg=true
    :target: https://ci.appveyor.com/project/Zulko/moviepy
    :alt: Build status on appveyor
.. image:: https://coveralls.io/repos/github/Zulko/moviepy/badge.svg?branch=master
    :target: https://coveralls.io/github/Zulko/moviepy?branch=master
    :alt: Code coverage from coveralls.io

MoviePy (full documentation_) is a Python library for video editing: cutting, concatenations, title insertions, video compositing (a.k.a. non-linear editing), video processing, and creation of custom effects. See the gallery_ for some examples of use.

MoviePy can read and write all the most common audio and video formats, including GIF, and runs on Windows/Mac/Linux, with Python 2.7+ and 3 (or only Python 3.4+ from v.1.0). Here it is in action in an IPython notebook:

.. image:: https://raw.githubusercontent.com/Zulko/moviepy/master/docs/demo_preview.jpeg
    :alt: [logo]
    :align: center

Example
-------

In this example we open a video file, select the subclip between t=50s and t=60s, add a title at the center of the screen, and write the result to a new file:

.. code:: python

    from moviepy.editor import *

    video = VideoFileClip("myHolidays.mp4").subclip(50,60)

    # Make the text. Many more options are available.
    txt_clip = ( TextClip("My Holidays 2013",fontsize=70,color='white')
                 .set_position('center')
                 .set_duration(10) )

    result = CompositeVideoClip([video, txt_clip]) # Overlay text on video
    result.write_videofile("myHolidays_edited.webm",fps=25) # Many options...


Maintainers wanted!
-------------------

As there are more and more people seeking support (320 open issues as of Sept. 2019!) and all the MoviePy maintainers seem busy, we'd love to hear about developers interested in giving a hand and solving some of the issues (especially the ones that affect you) or reviewing pull requests. Open an issue or contact us directly if you are interested. Thanks!

Installation
------------

MoviePy depends on the Python modules Numpy_, imageio_, Decorator_, and tqdm_, which will be automatically installed during MoviePy's installation. The software FFMPEG should be automatically downloaded/installed (by imageio) during your first use of MoviePy (installation will take a few seconds). If you want to use a specific version of FFMPEG, follow the instructions in ``config_defaults.py``. In case of trouble, provide feedback.

**Installation by hand:** download the sources, either from PyPI_ or, if you want the development version, from GitHub_, unzip everything into one folder, open a terminal and type:

.. code:: bash

    $ (sudo) python setup.py install

**Installation with pip:** if you have ``pip`` installed, just type this in a terminal:

.. code:: bash

    $ (sudo) pip install moviepy

If you have neither ``setuptools`` nor ``ez_setup`` installed, the command above will fail. In this case type this before installing:

.. code:: bash

    $ (sudo) pip install ez_setup


Optional but useful dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can install ``moviepy`` with all dependencies via:

.. code:: bash

    $ (sudo) pip install moviepy[optional]

ImageMagick_ is not strictly required, but needed if you want to incorporate texts. It can also be used as a backend for GIFs, though you can also create GIFs with MoviePy without ImageMagick.

Once you have installed ImageMagick, it will be automatically detected by MoviePy, **except on Windows!** Windows users, before installing MoviePy by hand, need to edit ``moviepy/config_defaults.py`` to provide the path to the ImageMagick binary, which is called `convert`. It should look like this:

.. code:: python

    IMAGEMAGICK_BINARY = "C:\\Program Files\\ImageMagick_VERSION\\convert.exe"

PyGame_ is needed for video and sound previews (not relevant if you intend to work with MoviePy on a server but essential for advanced video editing by hand).

For advanced image processing, you will need one or several of the following packages:

- The Python Imaging Library (PIL) or, even better, its branch Pillow_.
- Scipy_ (for tracking, segmenting, etc.) can be used to resize video clips if PIL and OpenCV are not installed.
- `Scikit Image`_ may be needed for some advanced image manipulation.
- `OpenCV 2.4.6`_ or a more recent version (one that provides the package ``cv2``) may be needed for some advanced image manipulation.
- `Matplotlib`_

Once you have installed it, ImageMagick will be automatically detected by MoviePy, (except for windows users and Ubuntu 16.04LTS users).

For Windows users, before installing MoviePy by hand, go into the ``moviepy/config_defaults.py`` file and provide the path to the ImageMagick binary called ``magick``. It should look like this:

.. code:: python

    IMAGEMAGICK_BINARY = "C:\\Program Files\\ImageMagick_VERSION\\magick.exe"

If you are using an older version of ImageMagick, keep in mind the name of the executable is not ``magick.exe`` but ``convert.exe``. In that case, the IMAGEMAGICK_BINARY property should be ``C:\\Program Files\\ImageMagick_VERSION\\convert.exe``

For Ubuntu 16.04LTS users, after installing MoviePy on the terminal, IMAGEMAGICK will not be detected by moviepy. This bug can be fixed. Modify the file in this directory: /etc/ImageMagick-6/policy.xml, comment out the statement <!-- <policy domain="path" rights="none" pattern="@*" /> -->.

PyGame_ is needed for video and sound previews (useless if you intend to work with MoviePy on a server but really essential for advanced video editing *by hand*).

For instance, using the method ``clip.resize`` requires that at least one of Scipy, PIL, Pillow or OpenCV is installed.


Documentation
-------------

Running `build_docs` has additional dependencies that require installation.

.. code:: bash

    $ (sudo) pip install moviepy[docs]

The documentation can be generated and viewed via:

.. code:: bash

    $ python setup.py build_docs

You can pass additional arguments to the documentation build, such as clean build:

.. code:: bash

    $ python setup.py build_docs -E

More information is available from the `Sphinx`_ documentation.

New in 1.0.0: Progress bars and messages with Proglog
-------------------------------------------------------

Non-backwards-compatible changes were introduced in 1.0.0 to
manage progress bars and messages using
`Proglog <https://github.com/Edinburgh-Genome-Foundry/Proglog>`_, which
enables to display nice progress bars in the console as well as in
a Jupyter notebook or any user interface, like a website.

To display notebook friendly progress bars, first install IPyWidgets:

.. code::

    sudo pip install ipywidgets
    sudo jupyter nbextension enable --py --sys-prefix widgetsnbextension

Then at the beginning of your notebook enter:

.. code:: python

    import proglog
    proglog.notebook()

Have a look at the Proglog project page for more options.

Running Tests
-------------

In order to run the test suite locally, first install the dependencies by navigating to the project directory and running:

.. code:: bash

    $ (sudo) pip install moviepy[test]

The test suite can then be executed via:

.. code:: bash

    $ pytest


Contribute
----------

MoviePy is open-source software originally written by Zulko_ and released under the MIT licence. The project is hosted on GitHub_, where everyone is welcome to contribute, ask for help or simply give feedback. Please read our `Contributing Guidelines`_ for more information about how to contribute!

You can also discuss the project on Reddit_ or Gitter_. These are preferred over GitHub issues for usage questions and examples.


Maintainers
-----------

- Zulko_ (owner)
- `@tburrows13`_
- `@mgaitan`_
- `@earney`_
- `@mbeacom`_
- `@overdrivr`_
- `@keikoro`_
- `@ryanfox`_


.. MoviePy links
.. _gallery: https://zulko.github.io/moviepy/gallery.html
.. _documentation: https://zulko.github.io/moviepy/
.. _`download MoviePy`: https://github.com/Zulko/moviepy
.. _`Label Wiki`: https://github.com/Zulko/moviepy/wiki/Label-Wiki
.. _Contributing Guidelines: https://github.com/Zulko/moviepy/blob/master/CONTRIBUTING.md

.. Websites, Platforms
.. _Reddit: https://www.reddit.com/r/moviepy/
.. _PyPI: https://pypi.python.org/pypi/moviepy
.. _GitHub: https://github.com/Zulko/moviepy
.. _Gitter: https://gitter.im/movie-py/Lobby

.. Software, Tools, Libraries
.. _Pillow: https://pillow.readthedocs.org/en/latest/
.. _Scipy: https://www.scipy.org/
.. _`OpenCV 2.4.6`: https://sourceforge.net/projects/opencvlibrary/files/
.. _Pygame: https://www.pygame.org/download.shtml
.. _Numpy: https://www.scipy.org/install.html
.. _imageio: https://imageio.github.io/
.. _`Scikit Image`: https://scikit-image.org/docs/stable/install.html
.. _Decorator: https://pypi.python.org/pypi/decorator
.. _tqdm: https://github.com/noamraph/tqdm
.. _ffmpeg: https://www.ffmpeg.org/download.html
.. _ImageMagick: https://www.imagemagick.org/script/index.php
.. _`Matplotlib`: https://matplotlib.org/
.. _`Sphinx`: https://www.sphinx-doc.org/en/master/setuptools.html

.. People
.. _Zulko: https://github.com/Zulko
.. _`@mgaitan`: https://github.com/mgaitan
.. _`@tburrows13`: https://github.com/tburrows13
.. _`@earney`: https://github.com/earney
.. _`@mbeacom`: https://github.com/mbeacom
.. _`@overdrivr`: https://github.com/overdrivr
.. _`@keikoro`: https://github.com/keikoro
.. _`@ryanfox`: https://github.com/ryanfox
