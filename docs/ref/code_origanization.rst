.. _codeorganization:

Organization of MoviePy's code
===============================

This reviews the folders and files in moviepy's code. It's very easy:

At the root of the project you have everything required for the packaging and installation of moviepy (README, setup.py, LICENCE) etc. Then you the ``docs/`` folder with the source code of the documentation, a folder for some :ref:`examples`, and the main folder ``moviepy/`` for the source code of the library itself.

The folder ``moviepy/`` the classes and modules relative to the video and the audio are clearly separated into two subfolders ``video/`` and ``audio/``. In ``moviepy/`` you will find all the classes, functions and decorations which are useful to both submodules ``audio`` and ``video``:

- ``Clip.py`` defines the base object for ``AudioClip`` and ``VideoClip`` and the simple methods that can be used by both, like ``clip.subclip``, ``clip.set_duration``, etc.
- Files ``config.py`` and ``config_defaults.py`` store the default paths to the external programs FFMPEG and ImageMagick.
- ``decorators.py`` provides very useful decorators that automatize some tasks, like the fact that some effects, when applied to a clip, should also be applied to it's mask, or to its audio track.
- ``tools.py`` provides misc. functions that are useful everywhere in the library, like a standardized call to subprocess, a time converter, a standardized way to print messages in the console, etc.
- ``editor.py`` is a helper module to easily load and initiate many functionalities of moviepy (see :ref:`efficient` for more details)

The submodules ``moviepy.audio`` and ``moviepy.video`` are organized approximately the same way: at their root they implement base classes (respectively ``AudioClip`` and ``VideoClip``) and they have the following submodules:

- ``io`` contains everything required to read files, write files, preview the clip or use a graphical interface of any sort. It contains the objects that speak to FFMEG and ImageMagick, the classes AudioFileClip and VideoFileClip, the functions used to preview a clip with pygame or to embed a video in HTML5 (for instance in the IPython Notebook).
- ``fx`` contains a collection of effects and filters (like turning a video black and white, correcting luminosity, zooming or creating a scrolling effect). To add an effect to MoviePy, you simply add a new file ``my_effect.py`` to this folder, and in the file you define the function ``my_effect(clip, *other_parameters)``.
- ``compositing`` contains functions and classes to compose videoclips (CompositeVideoClip, concatenate_videoclips, clips_array) 
- ``tools`` contains advanced tools that are not effects but can help edit clips or generate new clips (tracking, subtitles, etc.)