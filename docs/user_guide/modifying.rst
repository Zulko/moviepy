.. _modifying:

Modifying clips and apply effects
===================================

Of course, once you will have loaded a :py:class:`~moviepy.Clip.Clip` the next step of action will be to modify it to be able to integrate it in your final video.

To modify a clip, there is three main courses of actions :
 * The built-in methods of :py:class:`~moviepy.video.VideoClip.VideoClip` or :py:class:`~moviepy.audio.AudioClip.AudioClip` modifying the properties of the object.
 * The already-implemented effects of MoviePy you can apply on clips, usually affecting the clip by applying filters on each frame of the clip at rendering time.
 * The transformation filters that you can apply using :py:func:`~moviepy.Clip.Clip.transform` and :py:func:`~moviepy.Clip.Clip.time_transform`.


How modifications are applied to a clip ?
-------------------------------------------------------

Clip copy during modification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first thing you must know is that when modifying a clip, MoviePy **will never modify that clip directly**. 
Instead it will return **a modified copy of the original** and let the original untouched. This is known as out-place instead of in-place behavior.

To illustrate:

.. literalinclude:: /_static/code/user_guide/effects/modify_copy_example.py
    :language: python

This is an important point to understand, because it is one of the most recurrent source of bug for newcomers.


Memory consumption of effect and modifications 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When applying an effect or modification, it does not immediately apply the effect to all the frames of the clip, but only to the first frame: all the other frames will only be modified when required (that is, when you will write the whole clip to a file or when you will preview it). 

It means that creating a new clip is neither time nor memory hungry, all the computation happen during the final rendering.


Time representations in MoviePy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Many methods that we will see accept duration or timepoint as arguments. For instance :py:meth:`clip.subclipped(t_start, t_end) <moviepy.Clip.Clip.subclipped(t_start, t_end)>` which cuts the clip between two timepoints.

MoviePy usually accept duration and timepoint as either: 

* a number of seconds as a ``float``.
* a ``tuple`` with ``(minutes, seconds)`` or ``(hours, minutes, seconds)``.
* a ``string`` such as ``'00:03:50.54'``.

Also, you can usually provide negative times, indicating a time from the end of the clip. For example, ``clip.subclipped(-20, -10)`` cuts the clip between 20s before the end and 10s before the end.


Modify a clip using the ``with_*`` methods
-------------------------------------------------------

The first way to modify a clip is by modifying internal properties of your object, thus modifying his behavior.

These methods usually start with the prefix ``with_`` or ``without_``, indicating that they will return a copy of the clip with the properties modified.

So, you may write something like:

.. literalinclude:: /_static/code/user_guide/effects/using_with_methods.py
    :language: python

In addition to the ``with_*`` methods, a handful of very common methods are also accessible under shorter names:

- :py:meth:`~moviepy.video.VideoClip.VideoClip.resized`
- :py:meth:`~moviepy.video.VideoClip.VideoClip.crop`
- :py:meth:`~moviepy.video.VideoClip.VideoClip.rotate`

For a list of all those methods, see :py:class:`~moviepy.Clip.Clip` and :py:class:`~moviepy.video.VideoClip.VideoClip`.


.. _modifying#effects:

Modify a clip using effects 
---------------------------------

The second way to modify a clip is by using effects that will modify the frames of the clip (which internally are no more than `numpy arrays <https://numpy.org>`_)  by applying some sort of functions on them.

MoviePy come with many effects implemented in :py:mod:`moviepy.video.fx` for visual effects and :py:mod:`moviepy.audio.fx` for audio effects. 
For practicality, these two modules are loaded in MoviePy as ``vfx`` and ``afx``, letting you import them as ``from moviepy import vfx, afx``.

To use these effects, you simply need to instantiate them as object and apply them on your :py:class:`~moviepy.Clip.Clip` using method :py:meth:`~moviepy.Clip.Clip.with_effects`, with a list of :py:class:`~moviepy.Effect.Effect` objects you want to apply. 

For convenience the effects are also dynamically added as method of :py:class:`~moviepy.video.VideoClip.VideoClip` and :py:class:`~moviepy.video.AudioClip.AudioClip`  classes at runtime, letting you call them as simple method of your clip.

So, you may write something like:

.. literalinclude:: /_static/code/user_guide/effects/using_effects.py
    :language: python

.. note::
    MoviePy effects are automatically applied to both the sound and the mask of the clip if it is relevant, so that you don't have to worry about modifying these.

For a list of those effects, see :py:mod:`moviepy.video.fx` and :py:mod:`moviepy.audio.fx`.

In addition to the effects already provided by MoviePy, you can obviously :ref:`create_effects` and use them the same way.

.. _modifying#filters:

Modify a clip appearance and timing using filters
----------------------------------------------------------

In addition to modifying a clip's properties and using effects, you can also modify the appearance or timing of a clip by using your own custom *filters* with :py:func:`~moviepy.Clip.Clip.time_transform`, :py:func:`~moviepy.Clip.Clip.image_transform`, and more generally with :py:func:`~moviepy.Clip.Clip.transform`.

All these methods work by taking as first parameter a callback function that will receive either a clip frame, a timepoint, or both, and return a modified version of these.

Modify only the timing of a Clip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can change the timeline of the clip with :py:meth:`time_transform(your_filter) <moviepy.Clip.Clip.time_transform>`.
Where ``your_filter`` is a callback function taking clip time as a parameter and returning a new time:

.. literalinclude:: /_static/code/user_guide/effects/time_transform.py
    :language: python

Now the clip ``modified_clip1`` plays three times faster than ``my_clip``, while ``modified_clip2`` will be oscillating between 00:00:00 to 00:00:02 of ``my_clip``. Note that in the last case you have created a clip of infinite duration (which is not a problem for the moment).

.. note::
    By default :py:func:`~moviepy.Clip.Clip.time_transform` will only modify the clip main frame, without modifying clip audio or mask for :py:class:`~moviepy.video.VideoClip.VideoClip`. 
    
    If you wish to also modify audio and/or mask you can provide the parameter ``apply_to`` with either ``'audio'``, ``'mask'``, or ``['audio', 'mask']``. 


Modifying only the appearance of a Clip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For :py:class:`~moviepy.video.VideoClip.VideoClip`, you can change the appearance of the clip with :py:meth:`image_transform(your_filter) <moviepy.video.VideoClip.VideoClip.image_transform>`.
Where ``your_filter`` is a callback function, taking clip frame (a numpy array) as a parameter and returning the transformed frame:

.. literalinclude:: /_static/code/user_guide/effects/image_transform.py
    :language: python

Now the clip ``modified_clip1`` will have his green and blue canals inverted.

.. note::
    You can define if transformation should be applied to audio and mask same as for :py:func:`~moviepy.Clip.Clip.time_transform`.

.. note::
    Sometimes need to treat clip frames and mask frames in a different way. To distinguish between the two, you can always look at their shape, clips are ``H*W*3``, and masks ``H*W``.


Modifying both the appearance and the timing of a Clip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, you may want to process the clip by taking into account both the time and the frame picture, for example to apply visual effects variating with time. 
This is possible with the method :py:meth:`transform(your_filter) <moviepy.Clip.Clip.transform>`.
Where ``your_filter`` is a callback function taking two parameters, and returning a new frame picture. Where first argument is a ``get_frame`` method (i.e. a function ``get_frame(time)`` which given a time returns the clip’s frame at that time), and the second argument is the time.

.. literalinclude:: /_static/code/user_guide/effects/transform.py
    :language: python

This will scroll down the clip, with a constant height of 360 pixels.

.. note::
    You can define if transformation should be applied to audio and mask same as for :py:func:`~moviepy.Clip.Clip.time_transform`. 

.. note::
    When programming a new effect, whenever it is possible, prefer using ``time_transform`` and ``image_transform`` instead of ``transform`` when implementing new effects.
    The reason is that, though they both internally rely on ``transform`` when these effects are applied to ``ImageClip`` objects, MoviePy will recognize they only need to be applied once instead of on each frame, resulting in faster renderings.

To keep things simple, we have only addressed the case of :py:class:`~moviepy.video.VideoClip.VideoClip`, but know that the same principle applies to :py:class:`~moviepy.audio.AudioClip.AudioClip`, except that instead of a picture frame, you will have an audio frame, which is also a numpy array.
