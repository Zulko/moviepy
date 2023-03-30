"""Useful utilities working with MoviePy."""

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip


CLIP_TYPES = {
    "audio": AudioFileClip,
    "video": VideoFileClip,
    "image": ImageClip,
}


def close_all_clips(objects="globals", types=("audio", "video", "image")):
    """Closes all clips in a context.

    Follows different strategies retrieving the namespace from which the clips
    to close will be retrieved depending on the ``objects`` argument, and filtering
    by type of clips depending on the ``types`` argument.

    Parameters
    ----------

    objects : str or dict, optional
      - If is a string an the value is ``"globals"``, will close all the clips
        contained by the ``globals()`` namespace.
      - If is a dictionary, the values of the dictionary could be clips to close,
        useful if you want to use ``locals()``.

    types : Iterable, optional
      Set of types of clips to close, being "audio", "video" or "image" the supported
      values.
    """
    if objects == "globals":  # pragma: no cover
        objects = globals()
    if hasattr(objects, "values"):
        objects = objects.values()
    types_tuple = tuple(CLIP_TYPES[key] for key in types)
    for obj in objects:
        if isinstance(obj, types_tuple):
            obj.close()
