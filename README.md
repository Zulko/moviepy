# MoviePy


[![MoviePy page on the Python Package Index](https://badge.fury.io/py/moviepy.svg)](https://pypi.org/project/moviepy/) [![Discuss MoviePy on Gitter](https://img.shields.io/gitter/room/movie-py/gitter?color=46BC99&logo=gitter)](Gitter_) [![Build status on gh-actions](https://img.shields.io/github/actions/workflow/status/Zulko/moviepy/test_suite.yml?logo=github)](https://github.com/Zulko/moviepy/actions/workflows/test_suite.yml) [![Code coverage from coveralls.io](https://img.shields.io/coveralls/github/Zulko/moviepy/master?logo=coveralls)](https://coveralls.io/github/Zulko/moviepy?branch=master)

> [!NOTE]
> MoviePy recently upgraded to v2.0, introducing major breaking changes. You can consult the last v1 docs [here](https://zulko.github.io/moviepy/v1.0.3/) but beware that v1 is no longer maintained. For more info on how to update your code from v1 to v2, see [this guide](https://zulko.github.io/moviepy/getting_started/updating_to_v2.html).

MoviePy (online documentation [here](https://zulko.github.io/moviepy/)) is a Python library for video editing: cuts, concatenations, title insertions, video compositing (a.k.a. non-linear editing), video processing, and creation of custom effects.

MoviePy can read and write all the most common audio and video formats, including GIF, and runs on Windows/Mac/Linux, with Python 3.9+.

# Example

In this example we open a video file, select the subclip between 10 and
20 seconds, add a title at the center of the screen, and write the
result to a new file:

``` python
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# Load file example.mp4 and keep only the subclip from 00:00:10 to 00:00:20
# Reduce the audio volume to 80% of its original volume

clip = (
    VideoFileClip("long_examples/example2.mp4")
    .subclipped(10, 20)
    .with_volume_scaled(0.8)
)

# Generate a text clip. You can customize the font, color, etc.
txt_clip = TextClip(
    font="Arial.ttf",
    text="Hello there!",
    font_size=70,
    color='white'
).with_duration(10).with_position('center')

# Overlay the text clip on the first video clip
final_video = CompositeVideoClip([clip, txt_clip])
final_video.write_videofile("result.mp4")
```

# How MoviePy works

Under the hood, MoviePy imports media (video frames, images, sounds) and converts them into Python objects (numpy arrays) so that every pixel becomes accessible, and video or audio effects can be defined in just a few lines of code (see the [built-in effects]() for examples).

The library also provides ways to mix clips together (concatenations, playing clips side by side or on top of each other with transparency, etc.). The final clip is then encoded back into mp4/webm/gif/etc.

This makes MoviePy very flexible and approachable, albeit slower than using ffmpeg directly due to heavier data import/export operations.  


# Installation

Intall moviepy with `pip install moviepy`. For additional installation options, such as a custom FFMPEG or for previewing, see [this section](https://zulko.github.io/moviepy/getting_started/install.html). For development, clone that repo locally and install with `pip install -e .`

# Documentation

The online documentation ([here](https://zulko.github.io/moviepy/)) is automatically built at every push to the master branch. To build the documentation locally, install the extra dependencies via `pip install moviepy[doc]`, then go to the `docs` folder and run `make html`.

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

**Maintainers wanted!** this library has only been kept afloat by the involvement of its maintainers, and there are times where none of us have enough bandwidth. We'd love to hear about developers interested in giving a hand and solving some of the issues (especially the ones that affect you) or reviewing pull requests. Open
an issue or contact us directly if you are interested. Thanks!
