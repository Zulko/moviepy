Download and Installation
==========================


Core dependencies
-------------------

MoviePy cannot run without these dependencies:

- The software ffmpeg_ is needed for writing, reading, converting the sound and the video. 
- `Numpy`_ is needed for image and sound manipulation
- The Decorator_ module is used in the MoviePy code for better code readability

**Make sure to use a recent version of ffmpeg**. You can either install it or save the binary files in any folder and specify the path to these folders before installing MoviePy (for the latter, see `Manual installation`_ below).

**Debian and Ubuntu users**, you certainly have an out-of-date version of FFMPEG, you *must* download a recent version from the ffmpeg_ website.

Normally Numpy and Decorator will be automatically installed when you install MoviePy. In case of doubt/problem they can also be installed manually.
Numpy can be installed with most software managers on Linux distributions. Both Numpy and Decorator can be installed as follows with pip: ::

    (sudo) pip install decorator
    (sudo) pip install numpy

.. _pip_install:

Installation with PIP
------------------------

If you have ``pip`` installed, just type this in a terminal ::
    
    (sudo) pip install moviepy

.. _manual_install:

Manual installation
----------------------

You can install moviepy manually by downloading the sources, either on PYPI_ or (if you want the development version) on Github_ .

Then just unzip everything in one folder, open a terminal and type ::
    
    sudo python setup.py install

Before doing that, you should make sure that MoviePy can locate ffmpeg on your computer. To do that, run the script ``moviepy/conf.py``. It it fails, then you must enter the path to the FFMPEG executable in the first line of this file ::
    
    FFMPEG_BINARY = path/to/your/ffmpeg

 
(Not so) Optional dependencies
-------------------------------

You are not obliged to install these but for many uses MoviePy will scream at you and say that the package or the software is missing. All these dependencies can be installed any time after the installation of MoviePy.

- PyGame_ is needed for video and sound previews (really essential for advanced editing).
- imageMagick_  is needed for all text generation, GIF support, and much more in the future.

There are many packages for image manipulation/processing in python.  Most effects are coded such that none of these packages are needed, or such that having at least one of these packages is sufficient.

- Scipy is needed for many advanced functionalities (tracking, segmenting, etc.), and can be used for resizing video clips if PIL and OpenCV aren't installed on your computer.
- `Scikit Image`_ may be needed for some advanced image manipulation.
- The Python Imaging Library is not used yet (I don't like the copyright) but it is coming. 
- `OpenCV 2.4.6`_ (which provides the python package ``cv2``) or more recent may be needed for some advanced image manipulation. See below for the installation of OpenCV.

If you are on linux, these softwares will surely be in your repos.


Installing OpenCV 2.4.6
~~~~~~~~~~~~~~~~~~~~~~~~~

OpenCV is very optional, its installation is not always simple and I found it to be unstable, be warned !
The installation seems easy for Windows. On linux, here is what I found on the Internet:

- Remove any other version of OpenCV if you installed it through a package manager.
- Unzip the source code of `OpenCV 2.4.6`_ in some folder. open a terminal in this folder.
- Make a new directory and go into this directory: ::
      
      mkdir release
      cd release
      
- Run ``cmake``. Here is the line I used: ::
      
      cmake -D WITH_TBB=ON -D BUILD_NEW_PYTHON_SUPPORT=ON -D WITH_V4L=OFF -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=ON ..
      
- Run ``make``. This may take a few minutes (15 minutes on my computer). ::
      
      make
      
- Finally, install. ::
      
      sudo make install
      
And voilà !

You can check if it worked by opeing a Python console and typing ::
    
    import cv2
    print cv2.__version__

Advice: do not throw your ``release`` folder away. If later you have strange bugs with OpenCV involving ``.so`` files, just redo the ``sudo make install`` step.
    




.. _PYPI https://pypi.python.org/pypi/moviepy
.. _Github: https://github.com/Zulko/moviepy
.. _`OpenCV 2.4.6`: http://sourceforge.net/projects/opencvlibrary/files/
.. _Pygame: http://www.pygame.org/download.shtml
.. _`Numpy`: http://www.scipy.org/install.html
.. _`Scikit Image`: http://scikit-image.org/download.html
.. _Decorator: https://pypi.python.org/pypi/decorator


.. _ffmpeg: http://www.ffmpeg.org/download.html 
.. _imageMagick: http://www.imagemagick.org/script/index.php
