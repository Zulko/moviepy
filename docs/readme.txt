Installation
------------


MoviePy is very light (~1000 lines of code) but it uses many Python libraries
- `OpenCV 2.4.6`_ to read the movies
- PyGame_ for video/sound previews
- `Scipy and Numpy`_, for image/sound manipulation
- `Scikit Image`_ for advanced image manipulation 
- The Decorator_ module for better code readability

And needs some software:
- avconv, the "new ffmpeg", for writing movies and many useful operations.
- imageMagick for text generation (and much more in the future)

All these are normally easy to install (on linux, most of these will be in your repos).

Then you open a console in the moviepy source directory and type

    sudo python setup.py install

.. _`OpenCV 2.4.6`: http://sourceforge.net/projects/opencvlibrary/files/
.. _Pygame: http://www.pygame.org/download.shtml
.. _`Scipy and Numpy`: http://www.scipy.org/install.html
.. _`Scikit Image`: http://scikit-image.org/download.html
.. _Decorator: https://pypi.python.org/pypi/decorator

