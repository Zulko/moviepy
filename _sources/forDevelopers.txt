.. forDevs:

===============================
For developpers
===============================


TODO list
------------

Ideas of improvement (suggestions, help and commits are welcome !):

- Find users.
- Improve the ``set_pos`` functions, give it functionalities inspired from CSS/HTML, like margin-right, etc...
- Improve readability/naming.
- Make an installer for all the dependencies ?


Discussion of the dependencies
-------------------------------

I have found that complicated dependencies are a main reason why people get
discouraged by a software, so I take all the advices on the subject.


Movie writing
~~~~~~~~~~~~~~~~~~~~~~~

To write a movie, I used to generate pictures of the frames and then put them together using ffmpeg, because this is what matplotlib does. But it can be up to fifty times slower than writing the movie directly with OpenCV, and it is less memory efficient.

However, I like how you can tune the quality of the movie with ffmpeg, and I can't think of something else to merge sound and image. I know there is a war between ffmpeg/avconv/mencoder. I think ffmpeg is the most spread software. And no, it's not deprecated.

Movie rendering
~~~~~~~~~~~~~~~~~~~~~~~

For movie previews I am using Pygame instead of the original OpenCV frontend because Pygame
can also generate sound.
  

  
Movie and image manipulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The python package SimpleCV is an attempt at making OpenCV easier to use. It is totally cool, but the OpenCV devs are also trying to make it easier so they always make a lot of changes which break SimpleCV. They use the Python Imaging Library for image processing.

The package Wand (a Python binder for ImageMagick) is nice and is starting to accept numpy array images input/output.
   

Sound
~~~~~~~

The python package Pydub is really good but working with numpy arrays gives more freedom so I stick with Scipy.

