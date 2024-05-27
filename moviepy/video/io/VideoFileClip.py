"""Implements VideoFileClip, a class for video clips creation using video files."""

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.decorators import convert_path_to_string
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from moviepy.video.VideoClip import VideoClip


class VideoFileClip(VideoClip):
    """
    A video clip originating from a movie file. For instance: ::

        >>> clip = VideoFileClip("myHolidays.mp4")
        >>> clip.close()
        >>> with VideoFileClip("myMaskVideo.avi") as clip2:
        >>>    pass  # Implicit close called by context manager.


    Parameters
    ----------

    filename:
      The name of the video file, as a string or a path-like object.
      It can have any extension supported by ffmpeg:
      .ogv, .mp4, .mpeg, .avi, .mov etc.

    has_mask:
      Set this to 'True' if there is a mask included in the videofile.
      Video files rarely contain masks, but some video codecs enable
      that. For instance if you have a MoviePy VideoClip with a mask you
      can save it to a videofile with a mask. (see also
      ``VideoClip.write_videofile`` for more details).

    audio:
      Set to `False` if the clip doesn't have any audio or if you do not
      wish to read the audio.

    target_resolution:
      Set to (desired_width, desired_height) to have ffmpeg resize the frames
      before returning them. This is much faster than streaming in high-res
      and then resizing. If either dimension is None, the frames are resized
      by keeping the existing aspect ratio.

    resize_algorithm:
      The algorithm used for resizing. Default: "bicubic", other popular
      options include "bilinear" and "fast_bilinear". For more information, see
      https://ffmpeg.org/ffmpeg-scaler.html

    fps_source:
      The fps value to collect from the metadata. Set by default to 'fps', but
      can be set to 'tbr', which may be helpful if you are finding that it is reading
      the incorrect fps from the file.

    pixel_format
      Optional: Pixel format for the video to read. If is not specified
      'rgb24' will be used as the default format unless ``has_mask`` is set
      as ``True``, then 'rgba' will be used.

    is_mask
      `True` if the clip is going to be used as a mask.


    Attributes
    ----------

    filename:
      Name of the original video file.

    fps:
      Frames per second in the original file.


    Read docs for Clip() and VideoClip() for other, more generic, attributes.

    Lifetime
    --------

    Note that this creates subprocesses and locks files. If you construct one
    of these instances, you must call close() afterwards, or the subresources
    will not be cleaned up until the process ends.

    If copies are made, and close() is called on one, it may cause methods on
    the other copies to fail.

    """

    @convert_path_to_string("filename")
    def __init__(
        self,
        filename,
        decode_file=False,
        has_mask=False,
        audio=True,
        audio_buffersize=200000,
        target_resolution=None,
        resize_algorithm="bicubic",
        audio_fps=44100,
        audio_nbytes=2,
        fps_source="fps",
        pixel_format=None,
        is_mask=False,
    ):
        VideoClip.__init__(self, is_mask=is_mask)

        # Make a reader
        if not pixel_format:
            pixel_format = "rgba" if has_mask else "rgb24"
        self.reader = FFMPEG_VideoReader(
            filename,
            decode_file=decode_file,
            pixel_format=pixel_format,
            target_resolution=target_resolution,
            resize_algo=resize_algorithm,
            fps_source=fps_source,
        )

        # Make some of the reader's attributes accessible from the clip
        self.duration = self.reader.duration
        self.end = self.reader.duration

        self.fps = self.reader.fps
        self.size = self.reader.size
        self.rotation = self.reader.rotation

        self.filename = filename

        if has_mask:
            self.make_frame = lambda t: self.reader.get_frame(t)[:, :, :3]

            def mask_make_frame(t):
                return self.reader.get_frame(t)[:, :, 3] / 255.0

            self.mask = VideoClip(
                is_mask=True, make_frame=mask_make_frame
            ).with_duration(self.duration)
            self.mask.fps = self.fps

        else:
            self.make_frame = lambda t: self.reader.get_frame(t)

        # Make a reader for the audio, if any.
        if audio and self.reader.infos["audio_found"]:
            self.audio = AudioFileClip(
                filename,
                buffersize=audio_buffersize,
                fps=audio_fps,
                nbytes=audio_nbytes,
            )

    def __deepcopy__(self, memo):
        """Implements ``copy.deepcopy(clip)`` behaviour as ``copy.copy(clip)``.

        VideoFileClip class instances can't be deeply copied because the locked Thread
        of ``proc`` isn't pickleable. Without this override, calls to
        ``copy.deepcopy(clip)`` would raise a ``TypeError``:

        ```
        TypeError: cannot pickle '_thread.lock' object
        ```
        """
        return self.__copy__()

    def close(self):
        """Close the internal reader."""
        if self.reader:
            self.reader.close()
            self.reader = None

        try:
            if self.audio:
                self.audio.close()
                self.audio = None
        except AttributeError:  # pragma: no cover
            pass
