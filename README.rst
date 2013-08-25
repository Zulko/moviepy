MoviePy
========

MoviePy is Python module for script-based movie editing, which enables
basic operations (cuts, concatenations, title insertions) to be done
in a few lines. It can also be used for advanced compositing.

See the full documentation online here_ .


A typical MoviePy script looks like that: ::

    from moviepy import *
    
    # Load myHolidays.mp4 and select the subclip 00:00:50 - 00:00:60
    clip = MovieClip("myHolidays.mp4").subclip(50,60)
    
    # Generate a text clip (many options available ! )
    txt_clip = TextClip("My Holidays 2013",fontsize=70,color='white')
    txt_clip = txt_clip.set_pos(('center','center')).set_duration(10)
    
    # Overlay the text clip above the first clip
    video = CompositeVideoClip(clip.size, [clip, txt_clip])
    
    # write the result to a file in any format
    video.write("myHolidays_edited.avi",fps=25, codec='DIVX')
	
Download And Installation
--------------------------

You can `download MoviePy`_ on Github. Just unzip everything in one folder, open a terminal and type ::
    
    sudo python setup.py install

** This should install the python packages listed below, but NOT OpenCV, which you will have to download manually for the moment. **

MoviePy is a very small program but it relies on many existing Python packages:

- `OpenCV 2.4.6`_ or more recent, to read and write movie files. 
- PyGame_ for video and sound previews
- `Scipy and Numpy`_, for image and sound manipulation
- `Scikit Image`_ for advanced image manipulation 
- The Decorator_ module for better code readability



MoviePy also needs some external software:

- ffmpeg_, for writing movies and many other useful operations.
- imageMagick_ for text generation, GIF support, and much more in the future.

All these are normally easy to install (on linux, they will certainly be in your repos).

.. _here: http://zulko.github.io/moviepy/
.. _`download MoviePy`: https://github.com/Zulko/moviepy
.. _`OpenCV 2.4.6`: http://sourceforge.net/projects/opencvlibrary/files/
.. _Pygame: http://www.pygame.org/download.shtml
.. _`Scipy and Numpy`: http://www.scipy.org/install.html
.. _`Scikit Image`: http://scikit-image.org/download.html
.. _Decorator: https://pypi.python.org/pypi/decorator


.. _ffmpeg: http://www.ffmpeg.org/download.html 
.. _imageMagick: http://www.imagemagick.org/script/index.php
