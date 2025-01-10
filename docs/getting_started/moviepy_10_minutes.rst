.. _moviepy_10_minutes:

MoviePy in 10 Minutes: Creating a Trailer from "Big Buck Bunny"
===============================================================

.. note::
   This tutorial aims to be a simple and short introduction for new users wishing to use MoviePy. For a more in-depth exploration of the concepts seen in this tutorial, see :ref:`user_guide`.

In this tutorial, you will learn the basics of how to use the MoviePy library in just 10 minutes. As an example project for this tutorial, we will create the following trailer for the movie `"Big Buck Bunny." <https://peach.blender.org/>`_.

.. raw:: html

   <div style="position: relative; padding-bottom: 56.25%; padding-top: 30px; margin-bottom:30px; height: 0; overflow: hidden; margin-left: 5%;">
      <video controls>
         <source src="/moviepy/_static/medias/getting_started/moviepy_10_minutes/trailer_bbb.mp4" type="video/mp4">
         <p>Your browser does not support HTML5 video in MP4 format.</p>
      </video>
   </div>


Prerequisites
-------------

Before we start, make sure you have MoviePy installed. You can install it using pip:

.. code-block:: shell

   pip install moviepy


Also, we will need to gather a few resources such as the original movie, font files, images, etc.
To make it easy, we have prepared a template project you can download directly:

1. Download :download:`the project template </_static/medias/getting_started/moviepy_10_minutes/moviepy_10_minutes.zip>` and unzip it.
2. Take a look at the resources inside the folder to familiarize yourself.
3. Create a Python script file named ``trailer.py`` in the project directory.

Now, you are ready to proceed to the next steps.

Step 1: Import MoviePy and Load the Video
-----------------------------------------

Let's start by importing the necessary modules and loading the "Big Buck Bunny" video into our Python program:

.. literalinclude:: /_static/code/getting_started/moviepy_10_minutes/trailer.py
   :language: python
   :lines: 1-10

As you see, loading a video file is really easy, but MoviePy isn't limited to video. It can handle images, audio, texts, and even custom animations.

No matter the kind of resources, ultimately any clip will be either a :py:class:`~moviepy.video.VideoClip.VideoClip` for any visual element, and an :py:class:`~moviepy.audio.AudioClip.AudioClip` for any audio element.

In this tutorial, we will only see a few of those, but if you want to explore more, you can find an exhaustive list in the user guide about :ref:`loading`.

Step 2: Extract the Best Scenes
-------------------------------

To create our trailer, we will focus on presenting the main characters, so we need to extract parts of the movie.
This is a very classic task, so let's turn our main clip into multiple subclips:

.. literalinclude:: /_static/code/getting_started/moviepy_10_minutes/trailer.py
   :language: python
   :lines: 13-25


Here, we use the ``subclipped`` method to extract specific scenes from the main video. We provide the start and end times (in seconds or as text with the format ``HH:MM:SS.µS``) for each scene.
The extracted clips are stored in their respective variables (``intro_clip``, ``bird_clip``, etc.).

Step 3: Take a First Look with Preview
--------------------------------------

When editing videos, it's often essential to preview the clips to ensure they meet our vision. This allows you to watch the segment you're working on and make any necessary adjustments for the perfect result.

To do so using MoviePy, you can utilize the ``preview()`` function available for each clip (the complementary ``audio_preview()`` is also available for :py:class:`~moviepy.audio.AudioClip.AudioClip`).

.. note::
   Note that you will need ``ffplay`` installed and accessible to MoviePy for preview to work. You can check if ``ffplay`` is available by running the command ``python3 -c "from moviepy.config import check;check()"``.
   If not, please see :ref:`install#binaries`.

.. literalinclude:: /_static/code/getting_started/moviepy_10_minutes/trailer.py
   :language: python
   :lines: 28-38

By using the preview, you may have noticed that our clips not only contain video but also audio. This is because when loading a video, you not only load the image but also the audio tracks that are turned into :py:class:`~moviepy.audio.AudioClip.AudioClip` and
added to your video clip.

.. note::
   When previewing, you may encounter video slowing or video/audio shifting. This is not a bug; it's due to the fact that your computer cannot render the preview in real-time.
   In such a case, the best course of action is to set the ``fps`` parameter for the ``preview()`` at a lower value to make things easier on your machine.


Step 4: Modify a Clip by Cutting Out a Part of It
--------------------------------------------------

After previewing the clips, we notice that the rodents' scene is a bit long. Let's modify the clip by removing a specific part. It would be nice to remove parts of the scene that we don't need. This is also quite a common task in video-editing.
To do so, we are going to use the ``with_section_cut_out`` method to remove a portion of the clip between ``00:06:00`` to ``00:10:00``.

.. literalinclude:: /_static/code/getting_started/moviepy_10_minutes/trailer.py
   :language: python
   :lines: 41-54

In that particular case, we have used the ``with_section_cut_out``, but this is only one of the many clip manipulation methods starting with ``with_``. We will see a few others
in this tutorial, but we will miss a lot more. If you want an exhaustive list, go see :ref:`reference_manual`.

.. note::
   You may have noticed that we have reassigned the ``rodents_clip`` variable instead of just calling a method on it.
   This is because in MoviePy, any function starting with ``with_`` is out-of-place instead of in-place, meaning it does not modify the original data but instead copies it and modifies/returns the copy.
   So you need to store the result of the method and, if necessary, reassign the original variable to update your clip.


Step 5: Creating Text/Logo Clips
------------------------------------

In addition to videos, we often need to work with images and texts. MoviePy offers some specialized kinds of :py:class:`~moviepy.video.VideoClip.VideoClip` specifically for that purpose: ``ImageClip`` and ``TextClip``.

In our case, we want to create text clips to add text overlays between the video clips. We'll define the font, text content, font size, and color for each text clip. 
We also want to create image clips for the "Big Buck Bunny" logo and the "Made with MoviePy" logo and resize them as needed.

.. literalinclude:: /_static/code/getting_started/moviepy_10_minutes/trailer.py
    :language: python
    :lines: 56-82

As you can see, ``ImageClip`` is quite simple, but ``TextClip`` is a rather complicated object. Don't hesitate to explore the arguments it accepts.

.. note::
   In our example, we have used the ``resized()`` method to resize our image clips. This method works just like any ``with_*`` method, but because resizing is such a common
   task, the name has been shortened to ``resized()``. The same is true for ``cropped()`` and ``rotated()``.

Feel free to experiment with different effects and transitions to achieve the desired trailer effect.


Step 6: Timing the clips
--------------------------

We have all the clips we need, but if we were to combine all the clips into a single one using composition (we will see that in the next step), all our clips would start at the same time and play on top of each other, which is obviously not what we want.
Also, some video clips, like images and texts, have no endpoint/duration at creation (unless you have provided a duration parameter), which means trying to render them will throw an error as it would result in an infinite video.

To fix that, we need to specify when a clip should start and stop in the final clip. So, let's start by indicating when each clip must start and end using the appropriate with_* methods.

.. literalinclude:: /_static/code/getting_started/moviepy_10_minutes/trailer.py
    :language: python
    :lines: 85-111

.. note::
   By default, all clips have a start point at ``0``. If a clip has no ``duration`` but you set the ``end_time``, then the ``duration`` will be calculated for you. The reciprocity is also true.
   
   So in our case, we either use ``duration`` or ``end_time``, depending on what is more practical for each specific case.

Step 7: Seeing how all clips combine
--------------------------------------

Now that all our clips are timed, let's get a first idea of how our final clip will look. In video editing, the act of assembling multiple videos into a single one is known as composition.
So, MoviePy offers a special kind of :py:class:`~moviepy.video.VideoClip.VideoClip` dedicated to the act of combining multiple clips into one, the :py:class:`~moviepy.video.compositing.CompositeVideoClip.CompositeVideoClip`.

:py:class:`~moviepy.video.compositing.CompositeVideoClip.CompositeVideoClip` takes an array of clips as input and will play them on top of each other at render time, starting and stopping each clip at its start and end points.

.. note::
   If possible, :py:class:`~moviepy.video.compositing.CompositeVideoClip.CompositeVideoClip` will extract endpoint and size from the biggest/last ending clip. If a clip in the list has no duration, then you will have to manually set the duration of :py:class:`~moviepy.video.compositing.CompositeVideoClip.CompositeVideoClip` before rendering.

.. literalinclude:: /_static/code/getting_started/moviepy_10_minutes/trailer.py
    :language: python
    :lines: 114-136


Step 8: Positioning our clips
------------------------------

By looking at this first preview, we see that our clips are pretty well timed, but that the positions of our texts and logo are not satisfying. 

This is because, for now, we have only specified when our clips should appear, and not the position at which they should appear. By default, all clips are positioned from the top left of the video, at ``(0, 0)``.

All our clips do not have the same sizes (the texts and images are smaller than the videos), and the :py:class:`~moviepy.video.compositing.CompositeVideoClip.CompositeVideoClip` takes the size of the biggest clip (so in our case, the size of the videos), 
so the texts and images are all in the top left portion of the clip.

To fix this, we simply have to define the position of our clips in the composition with the method ``with_position``.

.. literalinclude:: /_static/code/getting_started/moviepy_10_minutes/trailer.py
    :language: python
    :lines: 139-174

.. note::
   The position is a tuple with horizontal and vertical position. You can give them as pixels, as strings (``top``, ``left``, ``right``, ``bottom``, ``center``), and even as a percentage by providing
   a float and passing the argument ``relative=True``.

Now, all our clips are in the right place and timed as expected.


Step 9: Adding transitions and effects
--------------------------------------------

So, our clips are timed and placed, but for now, the result is quite raw. It would be nice to have smoother transitions between the clips. 
In MoviePy, this is achieved through the use of effects.

Effects play a crucial role in enhancing the visual and auditory appeal of your video clips. Effects are applied to clips to create transitions, transformations, or modifications, resulting in better-looking videos. 
Whether you want to add smooth transitions between clips, alter visual appearance, or manipulate audio properties, MoviePy comes with many existing effects to help you bring your creative vision to life with ease. 

You can find these effects under the namespace ``vfx`` for video effects and ``afx`` for audio effects.

.. note::
   You can use audio effects on both audio and video clips because when applying audio effects to a video clip, the effect will actually be applied to the video clip's embedded audio clip instead.

Using an effect is very simple. You just have to call the method ``with_effects`` on your clip and pass an array of effect objects to apply.

In our case, we will add simple fade-in/out and cross-fade-in/out transitions between our clips, as well as slow down the ``rambo_clip``.

.. literalinclude:: /_static/code/getting_started/moviepy_10_minutes/trailer.py
    :language: python
    :lines: 177-239

Well, this looks a lot nicer! For this tutorial, we want to keep things simple, so we mostly used transitions. However, you can find many different effects and even create your own.
For a more in-depth presentation, see :py:mod:`moviepy.video.fx`, :py:mod:`moviepy.audio.fx`, and :ref:`create_effects`.

.. note::
   Looking at the result, you may notice that cross-fading makes clips go from transparent to opaque, and reciprocally, and wonder how it works.

   We won't get into details, but know that in MoviePy, you can declare some sections of a video clip to be transparent by using masks. Masks are nothing more than
   special kinds of video clips that are made of values ranging from ``0`` for a transparent pixel to ``1`` for a fully opaque one.

   For more info, see :ref:`loading#masks`.


Step 10: Modifying the appearance of a clip using filters
--------------------------------------------------------------

Finally, to make it more epic, we will apply a custom filter to our Rambo clip to make the image sepia. 
MoviePy does not come with a sepia effect out of the box, and creating a full custom effect is beyond the scope of this tutorial. However, we will see how we can apply a simple filter to our clip using the :py:meth:`~moviepy.video.VideoClip.VideoClip.image_transform` method.

To understand how filters work, you first need to understand that in MoviePy, a clip frame is nothing more than a numpy ``ndarray`` of shape ``HxWx3``.
This means we can modify how a frame looks like by applying simple math operations. Doing that on all the frames allows us to apply a filter to our clip!

The "apply to all frames" part is done by the ``image_transform`` method. This method takes a callback function as an argument, and at render time, it will trigger the callback for each frame of the clip, passing the current frame.

.. warning::
   This is a bit of an advanced usage, and the example involves matrix multiplication. If this is too much for you, you can simply ignore it until you really need to make custom filters, 
   then go look for a more detailed explanation on how to do filtering (:ref:`modifying#filters`) and create custom effects (:ref:`create_effects`) in the user guide.

   What you need to remember is just that we can apply filters on images. Here we do it mathematically, but you could very well use a library such as Pillow (provided it can understand numpy images) to do the maths for you!


.. literalinclude:: /_static/code/getting_started/moviepy_10_minutes/trailer.py
    :language: python
    :lines: 242-283


Step 11: Rendering the final clip to a file
--------------------------------------------

So, our final clip is ready, and we have made all the cutting and modifications we want. We are now ready to save the final result into a file. In video editing, this operation
is known as rendering.

Again, we will keep things simple and just do video rendering without much tweaking. In most cases, MoviePy and FFmpeg will automatically find the best settings. Take a look at :py:meth:`~moviepy.video.VideoClip.VideoClip.write_videofile` for more info.

.. literalinclude:: /_static/code/getting_started/moviepy_10_minutes/trailer.py
    :language: python
    :lines: 286-307


Conclusion
----------

Congratulations! You have successfully created a trailer for the movie "Big Buck Bunny" using the MoviePy library. This tutorial covered the basics of MoviePy, including loading videos, trimming scenes, adding effects and transitions, overlaying text, and even a little bit of filtering. 

If you want to dig deeper into MoviePy, we encourage you to try and experiment with this base example by using different effects, transitions, and audio elements to make your trailer truly captivating.
We also encourage you to go and read the :ref:`user_guide`, as well as looking directly at the :ref:`reference_manual`.
