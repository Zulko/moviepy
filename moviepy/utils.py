"""Useful utilities working with MoviePy."""

import moviepy.audio.io.ffmpeg_audiowriter as ffmpeg_audiowriter
import moviepy.video.io.ffmpeg_writer as ffmpeg_writer
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


def stop_processing_video(filename: str):
    """Use this to stop processing video in a multithreaded app.

    Parameters
    ----------
    filename:str
      stop processing video with this "filename".

    Examples
    --------
    >>> t=threading.Thread(target=
      lambda outputname:
      VideoFileClip("media/sintel_with_14_chapters.mp4")
      .write_videofile(outputname),
      args=["somename.mp4"])
    >>> t.start()
    >>> stop_processing_video('somename.mp4')
    """
    ffmpeg_writer.VIDEOS_TO_STOP[0] = True
    ffmpeg_writer.VIDEOS_TO_STOP.append(filename)

    ffmpeg_audiowriter.AUDIOS_TO_STOP.append(filename)
    ffmpeg_audiowriter.AUDIOS_TO_STOP[0] = True
