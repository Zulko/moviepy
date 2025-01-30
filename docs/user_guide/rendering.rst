.. _rendering:

Previewing and saving video clips
====================================

Once you are down working with your clips, the last step will be to export the result into a video/image file, or sometimes to simply preview it in order to verify everything is working as expected.

Previewing a clip
"""""""""""""""""""""

When you are working with a clip, you will frequently need to have a peak at what your clip looks like, either to verify that everything is working as intended, or to check how things looks.

To do so you could render your entire clip into a file, but that's a pretty long task, and you only need a quick look, so a better solution exists: previewing.

Preview a clip as a video
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::
    You must have ``ffplay`` installed and accessible to MoviePy to be able to use :py:func:`~moviepy.video.io.preview.preview`.
    If you'r not sure, take a look :ref:`install#binaries`

The first thing you can do is to preview your clip as a video, by calling method :py:func:`~moviepy.video.io.preview.preview` on your clip:

.. literalinclude:: /_static/code/user_guide/rendering/preview.py
    :language: python

You will probably frequently want to preview only a small portion of your clip, though ``preview`` do not offer such capabilities, you can easily emulate such behavior by using :py:meth:`~moviepy.Clip.Clip.subclipped`.

.. note::
    It is quite frequent for a clip preview to be out of sync, or to play slower than it should. It means that your computer is not powerful enough to render the clip in real time.
    
    Don't hesitate to play with the options of preview: for instance, lower the fps of the sound (11000 Hz is still fine) and the video. Also, downsizing your video with resize can help.

For more info, see :py:func:`~moviepy.video.io.preview.preview`.

.. note::
    A quite similar function is also available for :py:func:`~moviepy.audio.AudioClip.AudioClip`, see :py:func:`~moviepy.audio.io.ffplay_audiopreviewer.ffplay_audiopreview`.


Preview just one frame of a clip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In a lot of situation, you don't really need to preview your all clip, seeing only one frame is enough to see how it looks like and to make sure everything goes as expected.

To do so, you can use the method :py:func:`~moviepy.video.io.preview.show` on your clip, passing the frame time as an argument:

.. literalinclude:: /_static/code/user_guide/rendering/show.py
    :language: python

Contrary to video previewing, show does not require ``ffplay``, but use ``pillow`` ``Image.show`` function.

For more info, see :py:func:`~moviepy.video.io.preview.show`.


Showing a clip in Jupyter Notebook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you work with a `Jupyter Notebook <https://jupyter.org/>`_, it can be very practical to display your clip the notebook. To do so, you can use the method :py:func:`~moviepy.video.io.display_in_notebook.display_in_notebook` on your clip.

.. image:: /_static/medias/user_guide/demo_preview.jpeg
    :width: 500px
    :align: center

With :py:func:`~moviepy.video.io.display_in_notebook.display_in_notebook` you can embed videos, images and sounds, either from a file or directly from a clip:

.. literalinclude:: /_static/code/user_guide/rendering/display_in_notebook.py
    :language: python


.. warning::
    Know that :py:func:`~moviepy.video.io.display_in_notebook.display_in_notebook` will only work if it is on the last line a the notebook cell. 

    Also, note that :py:func:`~moviepy.video.io.display_in_notebook.display_in_notebook` actually embeds the clips physically in your notebook. The advantage is that you can move the notebook or put it online and the videos will work. 
    The drawback is that the file size of the notebook can become very large. Depending on your browser, re-computing and displaying at video many times can take some place in the cache and the RAM (it will only be a problem for intensive uses).
    Restarting your browser solves the problem.


For more info, see :py:func:`~moviepy.video.io.display_in_notebook.display_in_notebook`.


Save your clip into a file
""""""""""""""""""""""""""""""""""""""""

Once you are satisfied with how your clip looks, you can save it into a file, a step known in video edition as rendering. MoviePy offer various way to save your clip.

Video files (.mp4, .webm, .ogv...)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The obvious first choice will be to write your clip to a video file, which you can do with :py:meth:`~moviepy.video.VideoClip.VideoClip.write_videofile`: 

.. literalinclude:: /_static/code/user_guide/rendering/write_videofile.py
    :language: python

MoviePy can find the a default codec name for the most common file extensions. If you want to use exotic formats or if you are not happy with the defaults you can provide the codec with ``codec='mpeg4'`` for instance.

There are many many options when you are writing a video (bitrate, parameters of the audio writing, file size optimization, number of processors to use, etc.), and we will not go in details into each. So, for more info, see :py:meth:`~moviepy.video.VideoClip.VideoClip.write_videofile`.

.. note::
    Though you are encouraged to play with settings of ``write_videofile``, know that lowering the optimization preset or increasing the number of threads will not necessarily
    improve the rendering time, as the bottleneck may be on MoviePy computation of each frame and not in ffmpeg encoding.

    Also, know that it is possible to pass additional parameters to ffmpeg command line invoked by MoviePy by using the ``ffmpeg_params`` argument.

Sometimes it is impossible for MoviePy to guess the ``duration`` attribute of the clip (keep in mind that some clips, like ImageClips displaying a picture, have *a priori* an infinite duration). Then, the ``duration`` must be set manually with :py:meth:`~moviepy.Clip.Clip.with_duration`:

.. literalinclude:: /_static/code/user_guide/rendering/write_videofile_duration.py
    :language: python


.. note::
    A quite similar function is also available for :py:func:`~moviepy.audio.AudioClip.AudioClip`, see :py:func:`~moviepy.audio.io.AudioClip.write_audiofile`.


Export a single frame of the clip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As for previewing, sometimes you will need to export only one frame of a clip, for example to create the preview image of a video. You can do so with :py:meth:`~moviepy.video.VideoClip.VideoClip.save_frame`: 

.. literalinclude:: /_static/code/user_guide/rendering/save_frame.py
    :language: python

For more info, see :py:func:`~moviepy.video.VideoClip.VideoClip.save_frame`.


Animated GIFs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to writing video files, MoviePy also let you write GIF file with :py:meth:`~moviepy.video.VideoClip.VideoClip.write_gif`: 

.. literalinclude:: /_static/code/user_guide/rendering/write_gif.py
    :language: python


For more info, see :py:func:`~moviepy.video.VideoClip.VideoClip.write_gif`.


Export all the clip as images in a directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lastly, you may wish to export an entire clip as an image sequence (multiple images in one directory, one image per frame). You can do so with the function :py:meth:`~moviepy.video.VideoClip.VideoClip.write_images_sequence`: 

.. literalinclude:: /_static/code/user_guide/rendering/write_images_sequence.py
    :language: python

For more info, see :py:func:`~moviepy.video.VideoClip.VideoClip.write_images_sequence`.
