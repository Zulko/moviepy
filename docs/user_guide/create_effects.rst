.. _create_effects:

Creating your own effects
========================================================

In addition to the existing effects already offered by MoviePy, we can create our own effects to modify a clip however we want.


Why creating your own effects?
------------------------------------

For simple enough tasks, we've seen that we can :ref:`modifying#filters`. Though it might be enough for simple tasks, filters are kind of limited:

- They can only access frame and/or timepoint
- We cannot pass arguments to them
- They are hard to maintain and re-use

To allow for more complex and reusable clip modifications, we can create our own custom effects, that we will later apply with :py:func:`~moviepy.Clip.Clip.with_effects`.

For example, imagine we want to add a progress bar to a clip, to do so we will not only need the time and image of the current frame, but also the total duration of the clip.
We will also probably want to be able to pass parameters to define the appearance of the progress bar, such as color or height. This is a perfect task for an effect!


Creating an effect
--------------------

In MoviePy, effects are objects of type :py:class:`moviepy.Effect.Effect`, which is the base ``abstract class`` for all effects (kind of the same as :py:class:`~moviepy.Clip.Clip` is the base for all :py:class:`~moviepy.video.VideoClip.VideoClip` and :py:class:`~moviepy.audio.AudioClip.AudioClip`).

So, to create an effect, we will need to inherit the :py:class:`~moviepy.Effect.Effect` class, and do two things:

- Create an ``__init__`` method to be able to received the parameters of our effect.
- Implement the inherited :py:meth:`~moviepy.Effect.Effect.apply` method, which must take as an argument the clip we want to modify, and return the modified version.

In the end, your effect will probably use :py:func:`~moviepy.Clip.Clip.time_transform`, :py:func:`~moviepy.Clip.Clip.image_transform`, or :py:func:`~moviepy.Clip.Clip.transform` to really apply your modifications on the clip,
The main difference is, because your filter will be a method or an anonymous function inside your effect class, you will be able to access all properties of your object from it!

So, lets see how we could create our progress bar effect:

.. literalinclude:: /_static/code/user_guide/effects/custom_effect.py
    :language: python

.. note::
    When creating an effect, you frequently have to write boilerplate code for assigning properties on object initialization, ``dataclasses`` is a nice way to limit that.

If you want to create your own effects, in addition of this documentation we strongly encourage you to go and take a look at the existing ones (see :py:mod:`moviepy.video.fx` and :py:mod:`moviepy.audio.fx`) to see how they works and take inspiration.
    