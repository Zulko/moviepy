.. _rendering:

Previewing and Saving Video Clips
=================================

Once you are done working with your clips, the final step will be to export the result into a video/image file, or sometimes to simply preview it in order to verify that everything is working as expected.

Previewing a Clip
-----------------

When you are working with a clip, you will frequently need to have a quick look at what your clip looks like, either to verify that everything is working as intended or to check how things look.

To do so, you could render your entire clip into a file, but that's a rather long task, and you only need a quick look, so a better solution exists: previewing.

Preview a Clip as a Video
~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::
    You must have ``ffplay`` installed and accessible to MoviePy to be able to use :py:func:`~moviepy.video.io.preview.preview`.
    If you're not sure, take a look :ref:`install#binaries`

The first thing you can do is to preview your clip as a video by calling the method :py:func:`~moviepy.video.io.preview.preview` on your clip:

.. literalinclude:: /_static/code/user_guide/rendering/preview.py
    :language: python

You will probably frequently want to preview only a small portion of your clip, though ``preview`` does not offer such capabilities, you can easily emulate such behavior by using :py:meth:`~moviepy.Clip.Clip.subclip`.

.. note::
    It is quite frequent for a clip preview to be out of sync or to play slower than it should. This indicates that your computer is not powerful enough to render the clip in real-time.
    
    Don't hesitate to play with the options of preview: for instance, lower the fps of the sound (11000 Hz is still fine) and the video. Also, downsizing your video with :py:meth:`~moviepy.video.VideoClip.VideoClip.resize` can help.

For more information, see :py:func:`~moviepy.video.io.preview.preview`.

.. note::
    A quite similar function is also available for :py:func:`~moviepy.audio.AudioClip.AudioClip`, see :py:func:`~moviepy.audio.io.ffplay_audiopreviewer.ffplay_audiopreview`.

Preview Just One Frame of a Clip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In many situations, you don't really need to preview your entire clip; seeing just one frame is enough to see how it looks and to ensure everything is going as expected.

To do so, you can use the method :py:func:`~moviepy.video.io.preview.show` on your clip, passing the frame time as an argument:

.. literalinclude:: /_static/code/user_guide/rendering/show.py
    :language: python

Contrary to video previewing, :py:func:`~moviepy.video.io.preview.show` does not require ``ffplay`` but uses the ``pillow`` ``Image.show`` function.

For more information, see :py:func:`~moviepy.video.io.preview.show`.

Showing a Clip in Jupyter Notebook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you work with a `Jupyter Notebook <https://jupyter.org/>`_, it can be very practical to display your clip within the notebook. To do so, you can use the method :py:func:`~moviepy.video.io.display_in_notebook.display_in_notebook` on your clip.

.. image:: /_static/medias/user_guide/demo_preview.jpeg
    :width: 500px
    :align: center

With :py:func:`~moviepy.video.io.display_in_notebook.display_in_notebook`, you can embed videos, images, and sounds, either from a file or directly from a clip:

.. literalinclude:: /_static/code/user_guide/rendering/display_in_notebook.py
    :language: python

.. warning::
    Note that :py:func:`~moviepy.video.io.display_in_notebook.display_in_notebook` will only work if it is on the last line of the notebook cell. 

    Also, note that :py:func:`~moviepy.video.io.display_in_notebook.display_in_notebook` actually embeds the clips physically in your notebook. The advantage is that you can move the notebook or put it online and the videos will work. 
    However, the drawback is that the file size of the notebook can become very large. Depending on your browser, re-computing and displaying the video multiple times can take up space in the cache and the RAM (this will only be a problem for intensive uses).
    Restarting your browser solves the problem.

For more information, see :py:func:`~moviepy.video.io.display_in_notebook.display_in_notebook`.

Saving Your Clip into a File
----------------------------

Once you are satisfied with how your clip looks, you can save it into a file, a step known in video editing as rendering. MoviePy offers various ways to save your clip.

Video Files (.mp4, .webm, .ogv, ...)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The obvious first choice will be to write your clip to a video file, which you can do with :py:meth:`~moviepy.video.VideoClip.VideoClip.write_videofile`:

.. literalinclude:: /_static/code/user_guide/rendering/write_videofile.py
    :language: python

MoviePy can automatically find the default codec names for the most common file extensions. If you want to use exotic formats or if you are not happy with the defaults, you can provide the codec with ``codec='mpeg4'`` for instance.

There are many options when you are writing a video (bitrate, parameters of the audio writing, file size optimization, number of processors to use, etc.), and we will not go into detail about each. For more information, see :py:meth:`~moviepy.video.VideoClip.VideoClip.write_videofile`.

.. note::
    Although you are encouraged to experiment with the settings of ``write_videofile``, know that lowering the optimization preset or increasing the number of threads will not necessarily improve the rendering time, as the bottleneck may be in MoviePy's computation of each frame and not in ffmpeg encoding.

    Also, know that it is possible to pass additional parameters to the ffmpeg command line invoked by MoviePy by using the ``ffmpeg_params`` argument.

Sometimes it is impossible for MoviePy to guess the ``duration`` attribute of the clip (keep in mind that some clips, like ImageClips displaying a picture, have *a priori* an infinite duration). In such cases, the ``duration`` must be set manually with :py:meth:`~moviepy.Clip.Clip.with_duration`:

.. literalinclude:: /_static/code/user_guide/rendering/write_videofile_duration.py
    :language: python

.. note::
    A quite similar function is also available for :py:func:`~moviepy.audio.AudioClip.AudioClip`, see :py:func:`~moviepy.audio.io.AudioClip.write_audiofile`.

Export a Single Frame of the Clip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As with previewing, sometimes you will need to export only one frame of a clip, for example to create the preview image of a video. You can do so with :py:meth:`~moviepy.video.VideoClip.VideoClip.save_frame`:

.. literalinclude:: /_static/code/user_guide/rendering/save_frame.py
    :language: python

For more information, see :py:func:`~moviepy.video.VideoClip.VideoClip.save_frame`.

Animated GIFs
~~~~~~~~~~~~~

In addition to writing video files, MoviePy also lets you write GIF files with :py:meth:`~moviepy.video.VideoClip.VideoClip.write_gif`:

.. literalinclude:: /_static/code/user_guide/rendering/write_gif.py
    :language: python

For more information, see :py:func:`~moviepy.video.VideoClip.VideoClip.write_gif`.

Export All the Clip as Images in a Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lastly, you might wish to export an entire clip as an image sequence (multiple images in one directory, one image per frame). You can do so with the function :py:meth:`~moviepy.video.VideoClip.VideoClip.write_images_sequence`:

.. literalinclude:: /_static/code/user_guide/rendering/write_images_sequence.py
    :language: python

For more information, see :py:func:`~moviepy.video.VideoClip.VideoClip.write_images_sequence`.
```
