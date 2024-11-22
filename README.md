# MoviePy


[![MoviePy page on the Python Package Index](https://badge.fury.io/py/moviepy.svg)](https://pypi.org/project/moviepy/) [![Discuss MoviePy on Gitter](https://img.shields.io/gitter/room/movie-py/gitter?color=46BC99&logo=gitter)](Gitter_) [![Build status on gh-actions](https://img.shields.io/github/actions/workflow/status/Zulko/moviepy/test_suite.yml?logo=github)](https://github.com/Zulko/moviepy/actions/workflows/test_suite.yml) [![Code coverage from coveralls.io](https://img.shields.io/coveralls/github/Zulko/moviepy/master?logo=coveralls)](https://coveralls.io/github/Zulko/moviepy?branch=master)

> [!NOTE] 
> MoviePy recently upgraded to v2.0, introducing major
breaking changes. For more info on how to update your code for v2.0, see [this guide](https://zulko.github.io/moviepy/getting_started/updating_to_v2.html).

MoviePy (online documentation [here](https://zulko.github.io/moviepy/)) is a
Python library for video editing: cuts, concatenations, title
insertions, video compositing (a.k.a. non-linear editing), video
processing, and creation of custom effects.

MoviePy can read and write all the most common audio and video formats,
including GIF, and runs on Windows/Mac/Linux, with Python 3.9+.

# Example

In this example we open a video file, select the subclip between 10 and
20 seconds, add a title at the center of the screen, and write the
result to a new file:

``` python
# Import everything needed to edit video clips
from moviepy import *

# Load file example.mp4 and keep only the subclip from 00:00:10 to 00:00:20
clip = VideoFileClip("long_examples/example2.mp4").with_subclip(10, 20)

# Reduce the audio volume to 80% of its original volume
clip = clip.with_multiply_volume(0.8)

# Generate a text clip. You can customize the font, color, etc.
txt_clip = TextClip(font="example.ttf", text="Big Buck Bunny", font_size=70, color='white')

#The text clip should appear for 10s at the center of the screen
txt_clip = txt_clip.with_duration(10).with_position('center')

# Overlay the text clip on the first video clip
video = CompositeVideoClip([clip, txt_clip])

# Write the result to a file (many options available!)
video.write_videofile("result.mp4")
```

# Installation

Intall moviepy with `pip install moviepy`. For additional installation options, such as a custom FFMPEG or for previewing, see [this section](https://zulko.github.io/moviepy/getting_started/install.html). For development, clone that repo locally and install with `pip install -e .`

# Documentation

The online documentation is automatically built at every push to the master branch. To build the documentation locally, install the extra dependencies via `pip install moviepy[doc]`, then go to the `docs` folder and run `make html`.

# Contribute

MoviePy is open-source software originally written by
[Zulko](https://github.com/Zulko) and released under the MIT licence.
The project is hosted on [GitHub](https://github.com/Zulko/moviepy),
where everyone is welcome to contribute and open issues or give feedback Please read our [Contributing
Guidelines](https://github.com/Zulko/moviepy/blob/master/CONTRIBUTING.md).
To ask for help or simply discuss usage and examples, use [our Reddit channel](https://www.reddit.com/r/moviepy/).

# Maintainers

-   [Zulko](https://github.com/Zulko) (owner)
-   [@osaajani](https://github.com/OsaAjani) led the development of v2 ([MR](https://github.com/Zulko/moviepy/pull/2024))
-   [@tburrows13](https://github.com/tburrows13)
-   [@mgaitan](https://github.com/mgaitan)
-   [@earney](https://github.com/earney)
-   [@mbeacom](https://github.com/mbeacom)
-   [@overdrivr](https://github.com/overdrivr)
-   [@keikoro](https://github.com/keikoro)
-   [@ryanfox](https://github.com/ryanfox)
-   [@mondeja](https://github.com/mondeja)

# Maintainers wanted!

MoviePy is always looking for maintainers, and we'd love to hear about
developers interested in giving a hand and solving some of the issues
(especially the ones that affect you) or reviewing pull requests. Open
an issue or contact us directly if you are interested. Thanks!
