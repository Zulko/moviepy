"""Implements ``display_in_notebook``, a function to embed images/videos/audio in the
Jupyter Notebook.
"""

# Notes:
# All media are physically embedded in the Jupyter Notebook
# (instead of simple links to the original files)
# That is because most browsers use a cache system and they won't
# properly refresh the media when the original files are changed.

import inspect
import os
from base64 import b64encode

from moviepy.audio.AudioClip import AudioClip
from moviepy.tools import extensions_dict
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos
from moviepy.video.VideoClip import ImageClip, VideoClip


try:  # pragma: no cover
    from IPython.display import HTML

    ipython_available = True

    class HTML2(HTML):  # noqa D101
        def __add__(self, other):
            return HTML2(self.data + other.data)

except ImportError:

    def HTML2(content):  # noqa D103
        return content

    ipython_available = False


sorry = "Sorry, seems like your browser doesn't support HTML5 audio/video"
templates = {
    "audio": (
        "<audio controls>"
        "<source %(options)s  src='data:audio/%(ext)s;base64,%(data)s'>"
        + sorry
        + "</audio>"
    ),
    "image": "<img %(options)s src='data:image/%(ext)s;base64,%(data)s'>",
    "video": (
        "<video %(options)s"
        "src='data:video/%(ext)s;base64,%(data)s' controls>" + sorry + "</video>"
    ),
}


def html_embed(
    clip, filetype=None, maxduration=60, rd_kwargs=None, center=True, **html_kwargs
):
    """Returns HTML5 code embedding the clip.

    Parameters
    ----------

    clip : moviepy.Clip.Clip
      Either a file name, or a clip to preview.
      Either an image, a sound or a video. Clips will actually be
      written to a file and embedded as if a filename was provided.

    filetype : str, optional
      One of 'video','image','audio'. If None is given, it is determined
      based on the extension of ``filename``, but this can bug.

    maxduration : float, optional
      An error will be raised if the clip's duration is more than the indicated
      value (in seconds), to avoid spoiling the browser's cache and the RAM.

    rd_kwargs : dict, optional
      Keyword arguments for the rendering, like ``dict(fps=15, bitrate="50k")``.
      Allow you to give some options to the render process. You can, for
      example, disable the logger bar passing ``dict(logger=None)``.

    center : bool, optional
      If true (default), the content will be wrapped in a
      ``<div align=middle>`` HTML container, so the content will be displayed
      at the center.

    html_kwargs
      Allow you to give some options, like ``width=260``, ``autoplay=True``,
      ``loop=1`` etc.

    Examples
    --------
    .. code:: python

        from moviepy import *
        # later ...
        html_embed(clip, width=360)
        html_embed(clip.audio)

        clip.write_gif("test.gif")
        html_embed('test.gif')

        clip.save_frame("first_frame.jpeg")
        html_embed("first_frame.jpeg")
    """
    if rd_kwargs is None:  # pragma: no cover
        rd_kwargs = {}

    if "Clip" in str(clip.__class__):
        TEMP_PREFIX = "__temp__"
        if isinstance(clip, ImageClip):
            filename = TEMP_PREFIX + ".png"
            kwargs = {"filename": filename, "with_mask": True}
            argnames = inspect.getfullargspec(clip.save_frame).args
            kwargs.update(
                {key: value for key, value in rd_kwargs.items() if key in argnames}
            )
            clip.save_frame(**kwargs)
        elif isinstance(clip, VideoClip):
            filename = TEMP_PREFIX + ".mp4"
            kwargs = {"filename": filename, "preset": "ultrafast"}
            kwargs.update(rd_kwargs)
            clip.write_videofile(**kwargs)
        elif isinstance(clip, AudioClip):
            filename = TEMP_PREFIX + ".mp3"
            kwargs = {"filename": filename}
            kwargs.update(rd_kwargs)
            clip.write_audiofile(**kwargs)
        else:
            raise ValueError("Unknown class for the clip. Cannot embed and preview.")

        return html_embed(
            filename,
            maxduration=maxduration,
            rd_kwargs=rd_kwargs,
            center=center,
            **html_kwargs,
        )

    filename = clip
    options = " ".join(["%s='%s'" % (str(k), str(v)) for k, v in html_kwargs.items()])
    name, ext = os.path.splitext(filename)
    ext = ext[1:]

    if filetype is None:
        ext = filename.split(".")[-1].lower()
        if ext == "gif":
            filetype = "image"
        elif ext in extensions_dict:
            filetype = extensions_dict[ext]["type"]
        else:
            raise ValueError(
                "No file type is known for the provided file. Please provide "
                "argument `filetype` (one of 'image', 'video', 'sound') to the "
                "display_in_notebook function."
            )

    if filetype == "video":
        # The next lines set the HTML5-cvompatible extension and check that the
        # extension is HTML5-valid
        exts_htmltype = {"mp4": "mp4", "webm": "webm", "ogv": "ogg"}
        allowed_exts = " ".join(exts_htmltype.keys())
        try:
            ext = exts_htmltype[ext]
        except Exception:
            raise ValueError(
                "This video extension cannot be displayed in the "
                "Jupyter Notebook. Allowed extensions: " + allowed_exts
            )

    if filetype in ["audio", "video"]:
        duration = ffmpeg_parse_infos(filename, decode_file=True)["duration"]
        if duration > maxduration:
            raise ValueError(
                (
                    "The duration of video %s (%.1f) exceeds the 'maxduration'"
                    " attribute. You can increase 'maxduration', by passing"
                    " 'maxduration' parameter to display_in_notebook function."
                    " But note that embedding large videos may take all the memory"
                    " away!"
                )
                % (filename, duration)
            )

    with open(filename, "rb") as file:
        data = b64encode(file.read()).decode("utf-8")

    template = templates[filetype]

    result = template % {"data": data, "options": options, "ext": ext}
    if center:
        result = r"<div align=middle>%s</div>" % result

    return result


def display_in_notebook(
    clip,
    filetype=None,
    maxduration=60,
    t=None,
    fps=None,
    rd_kwargs=None,
    center=True,
    **html_kwargs,
):
    """Displays clip content in an Jupyter Notebook.

    Remarks: If your browser doesn't support HTML5, this should warn you.
    If nothing is displayed, maybe your file or filename is wrong.
    Important: The media will be physically embedded in the notebook.

    Parameters
    ----------

    clip : moviepy.Clip.Clip
      Either the name of a file, or a clip to preview. The clip will actually
      be written to a file and embedded as if a filename was provided.

    filetype : str, optional
      One of ``"video"``, ``"image"`` or ``"audio"``. If None is given, it is
      determined based on the extension of ``filename``, but this can bug.

    maxduration : float, optional
      An error will be raised if the clip's duration is more than the indicated
      value (in seconds), to avoid spoiling the browser's cache and the RAM.

    t : float, optional
      If not None, only the frame at time t will be displayed in the notebook,
      instead of a video of the clip.

    fps : int, optional
      Enables to specify an fps, as required for clips whose fps is unknown.

    rd_kwargs : dict, optional
      Keyword arguments for the rendering, like ``dict(fps=15, bitrate="50k")``.
      Allow you to give some options to the render process. You can, for
      example, disable the logger bar passing ``dict(logger=None)``.

    center : bool, optional
      If true (default), the content will be wrapped in a
      ``<div align=middle>`` HTML container, so the content will be displayed
      at the center.

    kwargs
      Allow you to give some options, like ``width=260``, etc. When editing
      looping gifs, a good choice is ``loop=1, autoplay=1``.

    Examples
    --------

    .. code:: python

        from moviepy import *
        # later ...
        clip.display_in_notebook(width=360)
        clip.audio.display_in_notebook()

        clip.write_gif("test.gif")
        display_in_notebook('test.gif')

        clip.save_frame("first_frame.jpeg")
        display_in_notebook("first_frame.jpeg")
    """
    if not ipython_available:
        raise ImportError("Only works inside an Jupyter Notebook")

    if rd_kwargs is None:
        rd_kwargs = {}

    if fps is not None:
        rd_kwargs["fps"] = fps

    if t is not None:
        clip = clip.to_ImageClip(t)

    return HTML2(
        html_embed(
            clip,
            filetype=filetype,
            maxduration=maxduration,
            center=center,
            rd_kwargs=rd_kwargs,
            **html_kwargs,
        )
    )
