Updating to v2.0
================

MoviePy v2.0 has undergone some large changes with the aim of making the API more consistent
and intuitive. There is a high likelihood that your pre-v2.0 programs will not run without
some changes. Almost all of the changes are 'surface-level', so usually all you'll need to do
is a "Find and Replace" on the class, method, and parameter names that have been changed.

Python 2
--------
MoviePy v2.0 only supports Python 3.6+ and **does not support Python 2**. So you will first
and foremost need to port your code from Python 2 to 3.

Imports
-------
It is generally no longer necessary to import from ``moviepy.editor``. It will still work, but
``moviepy.editor`` should now only be loaded if you are using MoviePy to edit videos *by hand*.

You should convert all of your imports to import directly from ``moviepy``, for example: ::

    from moviepy import VideoFileClip, concatenate_videoclips


See :ref:`should_i_use_moviepy_editor` for a more detailed explanation.


Renamings
---------
The most significant change has been renaming all ``.set_`` methods to ``.with_``. This is
to represent the fact that they work 'outplace', which means that they do not modify the
clip that they are applied to, instead returning a modified copy of the clip.

**The functionality has not been changed**, they have just been renamed to better reflect the existing
functionality.

TODO list all changed names here

TextClip & ImageMagick
----------------------
TODO explain changes once they've been merged