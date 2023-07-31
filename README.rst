MoviePy
=======

.. image:: https://badge.fury.io/py/moviepy.svg
    :target: PyPI_
    :alt: MoviePy page on the Python Package Index
.. image:: https://img.shields.io/gitter/room/movie-py/gitter?color=46BC99&logo=gitter
    :target: Gitter_
    :alt: Discuss MoviePy on Gitter
.. image:: https://img.shields.io/github/actions/workflow/status/Zulko/moviepy/test_suite.yml?logo=github
    :target: https://github.com/Zulko/moviepy/actions/workflows/test_suite.yml
    :alt: Build status on gh-actions
.. image:: https://img.shields.io/coveralls/github/Zulko/moviepy/master?logo=coveralls
    :target: https://coveralls.io/github/Zulko/moviepy?branch=master
    :alt: Code coverage from coveralls.io

> [!NOTE]
> MoviePy recently upgraded to v2.0, introducing major breaking changes, for more info, see `the updating guide <https://zulko.github.io/moviepy/getting_started/updating_to_v2.html>`_.


MoviePy (full documentation_) is a Python library for video editing: cutting, concatenations, title insertions, video compositing (a.k.a. non-linear editing), video processing, and creation of custom effects.

MoviePy can read and write all the most common audio and video formats, including GIF, and runs on Windows/Mac/Linux, with Python 3.7+.

Example
-------

In this example we open a video file, select the subclip between 10 and 20 seconds, add a title at the center of the screen, and write the result to a new file:

.. code:: python
    
    # Import everything needed to edit video clips
    from moviepy import *

    # Load file example.mp4 and extract only the subclip from 00:00:10 to 00:00:20
    clip = VideoFileClip("long_examples/example2.mp4").with_subclip(10, 20)

    # Reduce the audio volume to 80% of his original volume
    clip = clip.with_multiply_volume(0.8)

    # Generate a text clip. You can customize the font, color, etc.
    txt_clip = TextClip(font="example.ttf", text="Big Buck Bunny", font_size=70, color='white')

    # Say that you want it to appear for 10s at the center of the screen
    txt_clip = txt_clip.with_position('center').with_duration(10)

    # Overlay the text clip on the first video clip
    video = CompositeVideoClip([clip, txt_clip])

    # Write the result to a file (many options available!)
    video.write_videofile("result.mp4")

    

Maintainers wanted!
-------------------

MoviePy is always looking for maintainers, and we'd love to hear about developers interested in giving a hand and solving some of the issues (especially the ones that affect you) or reviewing pull requests. Open an issue or contact us directly if you are interested. Thanks!

Installation
------------

For standard installation, see documentation_install_.

For contributors installation, see documentation_dev_install_.


Documentation
-------------

Building the documentation has additional dependencies that require installation.

.. code:: bash

    $ (sudo) pip install moviepy[doc]

The documentation can be generated and viewed via:

.. code:: bash

    $ python setup.py build_docs

You can pass additional arguments to the documentation build, such as clean build:

.. code:: bash

    $ python setup.py build_docs -E

More information is available from the `Sphinx`_ documentation.



Contribute
----------

MoviePy is open-source software originally written by Zulko_ and released under the MIT licence. The project is hosted on GitHub_, where everyone is welcome to contribute, ask for help or simply give feedback. Please read our `Contributing Guidelines`_ for more information about how to contribute!

You can also discuss the project on Reddit_ or Gitter_. These are preferred over GitHub issues for usage questions and examples.


Maintainers
-----------

- Zulko_ (owner)
- `@tburrows13`_
- `@mgaitan`_
- `@earney`_
- `@mbeacom`_
- `@overdrivr`_
- `@keikoro`_
- `@ryanfox`_
- `@mondeja`_


.. MoviePy links
.. _documentation: https://zulko.github.io/moviepy/
.. _documentation_install: https://zulko.github.io/moviepy/getting_started/install.html
.. _documentation_dev_install: https://zulko.github.io/moviepy/developer_guide/developers_install.rst
.. _`download MoviePy`: https://github.com/Zulko/moviepy
.. _`Label Wiki`: https://github.com/Zulko/moviepy/wiki/Label-Wiki
.. _Contributing Guidelines: https://github.com/Zulko/moviepy/blob/master/CONTRIBUTING.md

.. Websites, Platforms
.. _Reddit: https://www.reddit.com/r/moviepy/
.. _PyPI: https://pypi.python.org/pypi/moviepy
.. _GitHub: https://github.com/Zulko/moviepy
.. _Gitter: https://gitter.im/movie-py/Lobby

.. Software, Tools, Libraries
.. _`Sphinx`: https://www.sphinx-doc.org/en/master/setuptools.html

.. People
.. _Zulko: https://github.com/Zulko
.. _`@mgaitan`: https://github.com/mgaitan
.. _`@tburrows13`: https://github.com/tburrows13
.. _`@earney`: https://github.com/earney
.. _`@mbeacom`: https://github.com/mbeacom
.. _`@overdrivr`: https://github.com/overdrivr
.. _`@keikoro`: https://github.com/keikoro
.. _`@ryanfox`: https://github.com/ryanfox
.. _`@mondeja`: https://github.com/mondeja
