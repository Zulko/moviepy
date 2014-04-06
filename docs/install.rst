Download and Installation
==========================

Core dependencies
-------------------

MoviePy requires the Python modules Numpy_, Decorator_, and tqdm_. All 
of these will be automatically installed during MoviePy's installation.

You will also need a **recent version** of the software ffmpeg_ , 
preferably downloaded directly from the ffmpeg website.

Installation
--------------

First method : if you have ``pip`` installed, just type this in a terminal (sudo is optional on some systems) ::
    
    (sudo) pip install moviepy

Second method : by hand. Download the sources, either on PyPI_ or (if you want the development version) on Github_, unzip everything in one folder, open a terminal and type ::
    
    (sudo) python setup.py install
    
Linking to ffmpeg
~~~~~~~~~~~~~~~~~~

If you put have a ffmpeg binary in you executable folder (on Linux it will be ``/usr/bin``) it will be detected automatically by MoviePy. Else make sure that MoviePy can locate ffmpeg on your computer by running the script ``moviepy/conf.py`` that is in the sources. It it fails, then you must enter the path to the FFMPEG executable in the first line of this file ::
    
    FFMPEG_BINARY = path/to/your/ffmpeg
    
Linking to ImageMagick (Windows only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the moment MoviePy cannot detect ImageMagick on Windows. You need 
to go into the ``moviepy/conf.py`` file and provide the path, it 
should look something like this ::
    
    IMAGEMAGICK_BINARY = "C:\Program Files\ImageMagick_VERSION\convert"


(Not so) Optional dependencies
-------------------------------

PyGame_ is needed for video and sound previews (useless if you intend to work with MoviePy on a server but really essential for advanced video editing).

ImageMagick_  is needed for all text generation, GIF import/export, and much more .

For advanced image processing you will need one or several of these packages. for instance ``clip.resize`` requires that at least one of Scipy, PIL, Pillow or OpenCV are installed.

- The Python Imaging Library (PIL) or, better, its branch Pillow_ .
- Scipy_ (for tracking, segmenting, etc.), and can be used for resizing video clips if PIL and OpenCV aren't installed on your computer.
- `Scikit Image`_ may be needed for some advanced image manipulation.
- `OpenCV 2.4.6`_ (provides the package ``cv2``) or more recent may be needed for some advanced image manipulation. See below.

If you are on linux, these softwares will surely be in your repos.


So you want to install OpenCV 2.4.6 ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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


