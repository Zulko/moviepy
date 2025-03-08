.. _updating_to_v2:

Updating from v1.X to v2.X
==========================

MoviePy v2.0 has undergone some large changes with the aim of making the API more consistent
and intuitive. As a result, multiple breaking changes have been made.
Therefore, there is a high likelihood that your pre-v2.0 programs will not run without
some changes.

Dropping support for Python 2
-----------------------------
Starting with version 2.0, MoviePy **no longer supports Python 2**, since Python 2 reached its end of life in 2020. 
Focusing on Python 3.7+ allows MoviePy to take advantage of the latest language features and improvements while maintaining code quality and security. 

Users are encouraged to upgrade to a supported version of Python to continue using MoviePy.

Suppression of ``moviepy.editor`` and simplified importation
------------------------------------------------------------
Before v2.0, it was advised to import from ``moviepy.editor`` whenever you needed to perform some manual operations,
such as previewing or hand editing, because the ``editor`` package handled a lot of magic and initialization, making your life
easier, at the cost of initializing some complex modules like ``pygame``.

With version 2.0, the ``moviepy.editor`` namespace no longer exists. Instead, you should import everything from ``moviepy`` like this:

.. code-block:: python

    from moviepy import *  # Simple and clean; the __all__ is set in moviepy, so only useful things will be loaded
    from moviepy import VideoFileClip  # You can also import only the things you really need

Renaming and API unification
-----------------------------

One of the most significant changes is the renaming of all ``.set_`` methods to ``.with_``. More generally, almost all methods that modify a clip now start
with ``with_``, indicating that they work 'out-of-place', meaning they do not directly modify the clip, but instead copy it, modify the copy, and return the updated copy,
leaving the original clip untouched.

We advise you to check your code for any calls to methods from ``Clip`` objects and verify if there is a matching ``.with_`` equivalent.

Massive refactoring of effects
------------------------------

With version 2.0, effects have undergone significant changes and refactoring. Although the logic of when and why to apply effects remains largely the same, 
the implementation has changed considerably.

If you used any kind of effects, you will need to update your code!

Moving effects from functions to classes
""""""""""""""""""""""""""""""""""""""""""""""

MoviePy version 2.0 introduces a more structured and object-oriented approach to handling effects. Previously, effects were simple Python functions that manipulated video clips or images. 
However, in version 2.0 and onwards, effects are now represented as classes.

This shift allows for better organization, encapsulation, and reusability of code, as well as more comprehensible code. Each effect is now encapsulated within its own class, making it easier to manage and modify. 

All effects now implement the :py:class:`~moviepy.Effect.Effect` abstract class, so if you ever wrote a custom effect.

If you ever wrote your own effect, you will have to migrate to the new object-based implementation. For more information, see :ref:`create_effects`.

Moving from ``clip.fx`` to :py:meth:`~moviepy.Clip.Clip.with_effects`
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

The move from functions to objects also meant that MoviePy dropped the method ``Clip.fx`` previously used to apply effects in favor of the new :py:meth:`~moviepy.Clip.Clip.with_effects`.

For more information on how to use effects with v2.0, see :ref:`modifying#effects`.

Removing effects as clip methods
""""""""""""""""""""""""""""""""""

Before version 2.0, when importing from ``moviepy.editor``, effects were added as clip class methods at runtime. This is no longer the case.

If you previously used effects by calling them as clip methods, you must now use :py:meth:`~moviepy.Clip.Clip.with_effects`.

Dropping many external dependencies and unifying the environment
-------------------------------------------------------------

With v1.0, MoviePy relied on many optional external dependencies, attempting to gracefully fall back from one library to another in the event one of them was missing, eventually dropping some features when no library was available.
This resulted in complex and hard-to-maintain code for the MoviePy team, as well as fragmented and hard-to-understand environments for users.

With v2.0, the MoviePy team aimed to offer a simpler, smaller, and more unified dependency list, focusing on ``Pillow`` for all complex image manipulation, and dropping altogether the usage of ``ImageMagick``, ``PyGame``, ``OpenCV``, ``scipy``, ``scikit``, and a few others.

Removed features
-----------------

Unfortunately, reducing the scope of MoviePy and limiting external libraries means that some features had to be removed. If you used any of the following features, you will have to create your own replacements:

- ``moviepy.video.tools.tracking``
- ``moviepy.video.tools.segmenting``
- ``moviepy.video.io.sliders``

Miscellaneous signature changes
-------------------------------

When updating the API and moving from previous libraries to ``Pillow``, some miscellaneous changes also occurred, meaning some method signatures may have changed.

You should check the new signatures if you used any of the following:

- ``TextClip``: Some argument names have changed, and a path to a font file is now needed at object instantiation.
- ``clip.resize`` is now ``clip.resized``.
- ``clip.crop`` is now ``clip.cropped``.
- ``clip.rotate`` is now ``clip.rotated``.
- Any previous ``Clip`` method not starting with ``with_`` now probably starts with it.

Why all these changes and updating from v1.0 to v2.0?
-----------------------------------------------------

You might wonder why all these changes were introduced. The answer is: time.

MoviePy has seen many evolutions since its first release and has become a complex project, with ambitions sometimes too large in relation to the available manpower on the development team.
Over time, as in any project, inconsistencies were introduced to support new functionalities without breaking the current API, and some initial choices no longer reflected the current state of things.

Due to multiple factors, MoviePy underwent a long period during which the main version distributed through PyPi diverged from the GitHub distributed version, causing confusion and chaos.

In an effort to simplify future development and limit confusion by providing a unified environment, it was decided to release a new major version including the many evolutions that happened over the years, which meant breaking changes, and thus a new major version was required.

For anyone interested in how and why all of these decisions were made, you can find much of the discussion in GitHub issues `#1874 <https://github.com/Zulko/moviepy/issues/1874>`_, `#1089 <https://github.com/Zulko/moviepy/issues/1089>`_ and `#2012 <https://github.com/Zulko/moviepy/issues/2012>`_.
