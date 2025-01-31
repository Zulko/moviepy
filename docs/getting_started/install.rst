.. _install:

Installation
==========================

Installation is done with ``pip``. If you don't have ``pip``, take a look at `how to install it <https://pip.pypa.io/en/stable/installation/>`_.

With ``pip`` installed, just type this in a terminal:

.. code:: bash

    $ (sudo) pip install moviepy


.. _install#binaries:

Installation of additional binaries
------------------------------------

MoviePy depends on the software ffmpeg_ for video reading and writing and on ``ffplay`` for video previewing.

You don't need to worry about ffmpeg_, as it should be automatically downloaded/installed by ImageIO during your first use of MoviePy (it takes a few seconds). 

You do need to worry about ``ffplay`` if you plan on using video/audio previewing. For these cases, make sure to have ``ffplay`` installed (it can usually be found alongside ``ffmpeg``) and 
make sure it is accessible to Python, or define a custom path (see below). 


Define custom paths to binaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to use a specific version of FFmpeg and FFplay, you can do so using environment variables.

There are a couple of environment variables used by MoviePy that allow you to configure custom paths to the external tools.

To setup any of these variables, the easiest way is to do it in Python before importing objects from MoviePy. For example:

.. code-block:: python

    import os
    os.environ["FFMPEG_BINARY"] = "/path/to/custom/ffmpeg"
    os.environ["FFPLAY_BINARY"] = "/path/to/custom/ffplay"


Alternatively, after installing the optional dependencies, you can create
a ``.env`` file in your working directory that will be automatically read.
For example

.. code-block:: ini

    FFMPEG_BINARY=/path/to/custom/ffmpeg
    FFPLAY_BINARY=/path/to/custom/ffplay


Environment variables
"""""""""""""""""""""""

There are 2 available environment variables for external binaries :

``FFMPEG_BINARY``
    Normally you can leave it to its default ('ffmpeg-imageio') in which
    case imageio will download the right ffmpeg binary (on first use) and then always use that binary.

    The second option is ``"auto-detect"``. In this case ffmpeg will be whatever
    binary is found on the computer: generally ``ffmpeg`` (on Linux/macOS) or ``ffmpeg.exe`` (on Windows).

    Lastly, you can set it to use a binary at a specific location on your disk by specifying the exact path.


``FFPLAY_BINARY``
    The default is ``"auto-detect"``. MoviePy will try to find and use the installed ``ffplay`` binary.

    You can set it to use a binary at a specific location on your disk. On Windows, this might look like::

        os.environ["FFPLAY_BINARY"] = r"C:\Program Files\ffmpeg\ffplay.exe"


Verify if MoviePy find binaries
""""""""""""""""""""""""""""""""
To test if FFmpeg and FFplay are found by MoviePy, in a Python console, you can run :

.. code-block:: python

    from moviepy.config import check
    check()


.. _ffmpeg: https://www.ffmpeg.org/download.html

