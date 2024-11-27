.. _updating_to_v2:

Updating from v1.X to v2.X
==========================

MoviePy v2.0 has undergone some large changes with the aim of making the API more consistent
and intuitive. In order to do so multiple breaking changes have been made.
Therefore, there is a high likelihood that your pre-v2.0 programs will not run without
some changes.

Dropping support of Python 2
-----------------------------
Starting with version 2.0, MoviePy **no longer supports Python 2**, since Python 2 reached its end of life in 2020. 
Focusing on Python 3.7+ allows MoviePy to take advantage of the latest language features and improvements while maintaining code quality and security. 

Users are encouraged to upgrade to a supported version of Python to continue using MoviePy.

``moviepy.editor`` suppression and simplified importation
---------------------------------------------------------
Before v2.0, it was advised to import from ``moviepy.editor`` whenever you needed to do some sort of manual operations,
such as previewing or hand editing, because the ``editor`` package handled a lot of magic and initialization, making your life
easier, at the cost of initializing some complex modules like ``pygame``.

With version 2.0, the ``moviepy.editor`` namespace simply no longer exists. You simply import everything from ``moviepy`` like this: :: 
    
    from moviepy import * # Simple and nice, the __all__ is set in moviepy so only useful things will be loaded
    from moviepy import VideoFileClip # You can also import only the things you really need


Renaming and API unification
------------------------------

One of the most significant change has been renaming all ``.set_`` methods to ``.with_``. More generally, almost all the method modifying a clip now starts
by ``with_``, indicating that they work 'outplace', meaning they do not directly modify the clip, but instead copy it, modify this copy, and return the updated copy,
leaving the original clip untouched.

We advise you to check in your code for any call of method from ``Clip`` objects and check for a matching ``.with_`` equivalent. 


Massive refactoring of effects
-------------------------------

With version 2.0, effects have undergone massive changes and refactoring. Though the logic of why and when applying effects remain globally the same, 
the implementation changed quite heavily.

If you used any kind of effects, you will have to update your code!

Moving effects from function to classes
""""""""""""""""""""""""""""""""""""""""""""""

MoviePy version 2.0 introduces a more structured and object-oriented approach to handling effects. In previous versions, effects were simply Python functions that manipulated video clips or images. 
However, in version 2.0 and onwards, effects are now represented as classes.

This shift allows for better organization, encapsulation, and reusability of code, as well as more comprehensible code. Each effect is now encapsulated within its own class, making it easier to manage and modify. 

All effects are now implementing the :py:class:`~moviepy.Effect.Effect` abstract class, so if you ever used any custom effect.

If you ever write your own effect, you will have to migrate to the new object implementation. For more info see :ref:`create_effects`.

Moving from ``clip.fx`` to :py:meth:`~moviepy.Clip.Clip.with_effects`
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Moving from function to object also meant MoviePy had to drop the method ``Clip.fx`` previously used to apply effects in favor of the new :py:meth:`~moviepy.Clip.Clip.with_effects`.

For more info about how to use effects with v2.0, see :ref:`modifying#effects`.

Removing effects as clip methods
""""""""""""""""""""""""""""""""""

Before version 2.0, when importing from ``moviepy.editor`` the effects was added as clip class method at runtime. This is no longer the case.

If you previously used effect by calling them as clips method, you must now use :py:meth:`~moviepy.Clip.Clip.with_effects`.

Dropping many external dependencies and unifying environment
-------------------------------------------------------------

With v1.0, MoviePy relied on many optional external dependencies, trying to gracefully fallback from one library to another in the event one of them was missing, eventually dropping some features when no library was available.
This resulted in complex and hard to maintain code for the MoviePy team, as well as fragmented and hard to understand environment for the users.

With v2.0 the MoviePy team tried to offer a simpler, smaller and more unified dependency list, with focusing on ``pillow`` for all complex image manipulation, and dropping altogether the usage of ``ImageMagick``, ``PyGame``, ``OpenCV``, ``scipy``, ``scikit``, and a few others.

Removed features
-----------------

Sadly, reducing the scope of MoviePy and limiting the external libraries mean that some features had to be removed, if you used any of the following features, you will have to create your own replacement:

- ``moviepy.video.tools.tracking``
- ``moviepy.video.tools.segmenting``
- ``moviepy.video.io.sliders``

Miscellaneous signature changes
------------------------------

When updating the API and moving from previous libraries to ``pillow``, some miscellaneous changes also happen, meaning some methods signatures may have changed.

You should check the new signatures if you used any of the following:

- ``TextClip`` some arguments named have changed and a path to a font file is now needed at object instantiation
- ``clip.resize`` is now ``clip.resized``
- ``clip.crop`` is now ``clip.cropped``
- ``clip.rotate`` is now ``clip.rotated``
- Any previous ``Clip`` method not starting by ``with_`` now probably start with it


Why all these changes and updating from v1.0 to v2.0?
-------------------------------------------------------

You may ask yourself why were all these changes introduced? The answer is: time.

MoviePy have seen many evolution since his first release and have became kind of a complex project, with ambitions sometimes too important in regards to available manpower on the development team.
Over time, as in any project, inconsistencies have been introduced in order to support new functionalities without breaking current API, and some initial choices no longer reflected the current state of things.

Due to multiple factors, MoviePy have also undergone a long period of time during which the main version distributed through PiPy diverged from the GitHub distributed version, introducing confusion and chaos.

In a global effort to simplify future development and limit confusion by providing a unified environment, it has been decided to release a new major version including the many evolutions than happened over the years, which meant breaking changes, and so a new major version released was required.

For anyone interested in how and why all of these things have been decided, you can find a lot of the discussion that went into this in GitHub issues `#1874 <https://github.com/Zulko/moviepy/issues/1874>`_, `#1089 <https://github.com/Zulko/moviepy/issues/1089>`_ and `#2012 <https://github.com/Zulko/moviepy/issues/2012>`_.