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


Arabic or Hebrew text in a TextClip is reversed, or its letters are not joined
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Known reason: :py:class:`~moviepy.video.VideoClip.TextClip` draws text with Pillow, which
only joins Arabic letters and lays out right-to-left text when it can use Raqm. Pillow's
wheels need the FriBiDi library, installed separately, for that. You can check with::

    python -c "from PIL import features; print(features.check('raqm'))"

If it prints ``False``, you can either:

* install FriBiDi, for instance with ``sudo apt install libfribidi0`` on Debian and Ubuntu.
  On Windows, see `Pillow's installation notes`_. On Apple Silicon Macs, Pillow does not
  look in Homebrew's ``/opt/homebrew/lib``, so ``brew install fribidi`` alone is not enough.
* or use a text clip that shapes the text itself, such as the drop-in ``TextClip`` from khatt_.

The common workaround of passing the text through ``arabic_reshaper`` and ``python-bidi``
first only works while Raqm is missing: once Pillow can use Raqm, the text is processed
twice and comes out reversed again.

.. _Github: https://github.com/Zulko/moviepy
.. _Subreddit: https://www.reddit.com/r/moviepy/
.. _Pillow's installation notes: https://pillow.readthedocs.io/en/stable/installation/building-from-source.html#external-libraries
.. _khatt: https://github.com/DrEssam97/khatt

