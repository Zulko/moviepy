FAQ and troubleshooting
=========================

This section intend to answer the most common questions and errors.

Common errors that are not bugs
--------------------------------

These are very common errors which are not considered as bugs to be
solved (but you can still ask for this to change). If these answers
don't work for you, please open a bug report on Github_, or on the dedicated Subreddit_.


MoviePy generated a video that cannot be read by my favorite player.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Known reason: one of the video's dimensions were not even,
for instance 720x405, and you used a MPEG4 codec like libx264 (default
in MoviePy). In this case the video generated uses a format that is
readable only on some readers like VLC.


I can't seem to read any video with MoviePy
""""""""""""""""""""""""""""""""""""""""""""""

Known reason: you have a deprecated version of FFmpeg, install a recent version from the
website, not from your OS's repositories! (see :ref:`install`).


Previewing videos make them slower than they are
"""""""""""""""""""""""""""""""""""""""""""""""""

It means that your computer is not good enough to render the clip in real time. Don't hesitate to play with the options of ``preview``: for instance, lower the fps of the sound (11000 Hz is still fine) and the video. Also, downsizing your video with ``resize`` can help.

.. _Github: https://github.com/Zulko/moviepy
.. _Subreddit: https://www.reddit.com/r/moviepy/

