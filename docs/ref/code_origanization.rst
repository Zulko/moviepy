.. _codeorganization:

Organization of MoviePy's code
===============================

At the root of the project you have everything required for the packaging and installation of MoviePy (README, setup.py, LICENCE) etc. Then you have the ``docs/`` folder with the source code of the documentation, a folder for some :ref:`examples`, and the main folder ``moviepy/`` for the source code of the library itself.

The folder ``moviepy/`` the classes and modules relative to the video and the audio are clearly separated into two subfolders: ``video/`` and ``audio/``.

In ``moviepy/`` you will find all the classes, functions and decorations which are useful to both submodules ``audio`` and ``video``:

- ``Clip.py`` defines the base object (that ``AudioClip`` and ``VideoClip`` both inherit from) and the simple methods that can be used by both, like ``clip.subclip``, ``clip.with_duration``, etc.
- ``config.py`` handles the paths to the external programs FFmpeg and ImageMagick.
- ``decorators.py`` provides very useful decorators that automate some tasks, like the fact that some effects, when applied to a clip, should also be applied to its mask or to its audio track.
- ``tools.py`` provides miscellaneous functions that are useful everywhere in the library, like a standardized call to subprocess, a time converter, and an extension to codec lookup table.
- ``editor.py`` is a helper module that imports functionality that you need for editing by hand (see :ref:`efficient` for more details).

The submodules ``moviepy.audio`` and ``moviepy.video`` are organized approximately the same way: at their root they implement base classes (``AudioClip`` and ``VideoClip`` respectively) and they have the following submodules:

- ``io`` contains everything required to read files, write files, preview the clip or use a graphical interface of any sort. It contains the objects that speak to FFmpeg and ImageMagick, the classes ``AudioFileClip`` and ``VideoFileClip``, the functions used to preview a clip with pygame or to embed a video in HTML5 (for instance in the IPython Notebook).
- ``fx`` contains a collection of effects and filters (like turning a video black and white, correcting luminosity, zooming or creating a scrolling effect).
- ``compositing`` contains functions and classes to combine videoclips (``CompositeVideoClip``, ``concatenate_videoclips``, ``clips_array``)
- ``tools`` contains advanced tools that are not effects but can help edit clips or generate new clips (tracking, subtitles, etc.)