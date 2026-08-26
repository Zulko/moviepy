"""Implements VideoFileClip, a class for video clips creation using video files."""

import os

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.decorators import convert_path_to_string
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader, ffmpeg_parse_infos
from moviepy.video.VideoClip import VideoClip


class VideoFileClip(VideoClip):
    """A video clip originating from a movie file. For instance:

    .. code:: python

        clip = VideoFileClip("myHolidays.mp4")
        clip.close()
        with VideoFileClip("myMaskVideo.avi") as clip2:
            pass  # Implicit close called by context manager.


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

    audio_stream_index
      The index of the audio stream to read from the file.


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
        audio_stream_index=0,
    ):
        VideoClip.__init__(self, is_mask=is_mask)

        # Make a reader
        if not pixel_format:
            pixel_format = "rgba" if has_mask else "rgb24"

        # Backend selection is internal-only and does not change the public API.
        # When unset, default to 'auto': prefer OpenCV (with hwaccel attempt)
        # then fall back to ffmpeg.
        backend = (os.getenv("MOVIEPY_VIDEO_READER") or "auto").strip().lower()

        infos = ffmpeg_parse_infos(
            filename,
            check_duration=True,
            fps_source=fps_source,
            decode_file=decode_file,
            print_infos=False,
        )

        def _env_flag(name: str, default: str = "0") -> bool:
            val = os.environ.get(name, default)
            return str(val).strip().lower() not in {"0", "false", "no", "off", ""}

        def _try_make_true_gpu_reader():
            """Best-effort GPU-resident decode reader.

            This is internal-only and should never change public MoviePy APIs.
            It activates automatically when a usable CUDA/CuPy runtime is
            available (unless explicitly disabled), and will fall back safely.
            """
            if _env_flag("MOVIEPY_DISABLE_GPU_DECODE", "0"):
                raise RuntimeError("GPU decode disabled")

            # Keep alpha/mask semantics conservative; GPU decode backends
            # typically don't preserve alpha.
            if has_mask or is_mask:
                raise RuntimeError("GPU decode not used for alpha/mask clips")

            if str(pixel_format).lower() != "rgb24":
                raise RuntimeError("GPU decode backend only supports rgb24")

            # If the caller asked ffmpeg to resize, preserve that behavior by
            # using the existing readers.
            if (target_resolution is not None) and (None in target_resolution):
                raise RuntimeError(
                    "GPU decode backend requires explicit target_resolution"
                )

            # Auto-enable when CUDA/CuPy is usable.
            # (GPU render may still be disabled; decode can still be GPU-first.)
            from moviepy.video.tools import cupy_utils, gpu_render

            if not (gpu_render.is_enabled() and gpu_render.is_available()):
                if not cupy_utils.is_cupy_usable():
                    raise RuntimeError("CUDA/CuPy runtime not usable")

            backend = (
                (os.getenv("MOVIEPY_GPU_DECODE_BACKEND") or "auto").strip().lower()
            )
            if backend in {"0", "false", "off", "none", "disable", "disabled"}:
                raise RuntimeError("GPU decode backend disabled")

            # Auto backend: try decord first.
            if backend in {"auto", "decord", "nvdec"}:
                from moviepy.video.io.decord_gpu_reader import DecordGPUVideoReader

                ctx_id = int(os.getenv("MOVIEPY_GPU_DEVICE", "0"))
                return DecordGPUVideoReader(
                    filename,
                    infos=infos,
                    target_resolution=target_resolution,
                    pixel_format=pixel_format,
                    resize_algo=resize_algorithm,
                    ctx_id=ctx_id,
                )

            raise RuntimeError(f"Unknown MOVIEPY_GPU_DECODE_BACKEND={backend!r}")

        def _make_ffmpeg_reader():
            return FFMPEG_VideoReader(
                filename,
                decode_file=decode_file,
                pixel_format=pixel_format,
                target_resolution=target_resolution,
                resize_algo=resize_algorithm,
                fps_source=fps_source,
                infos=infos,
            )

        def _try_make_opencv_reader():
            from moviepy.video.io.opencv_reader import OpenCV_VideoReader

            # First try with hwaccel hints, then without.
            try:
                return OpenCV_VideoReader(
                    filename,
                    decode_file=decode_file,
                    pixel_format=pixel_format,
                    target_resolution=target_resolution,
                    resize_algo=resize_algorithm,
                    fps_source=fps_source,
                    infos=infos,
                    prefer_hwaccel=True,
                )
            except Exception:
                return OpenCV_VideoReader(
                    filename,
                    decode_file=decode_file,
                    pixel_format=pixel_format,
                    target_resolution=target_resolution,
                    resize_algo=resize_algorithm,
                    fps_source=fps_source,
                    infos=infos,
                    prefer_hwaccel=False,
                )

        force_ffmpeg = backend in {"ffmpeg", "pipe"}
        force_opencv = backend in {"opencv", "cv2"}
        is_auto = backend in {"", "auto"}

        can_use_opencv = (
            (not os.getenv("MOVIEPY_DISABLE_OPENCV"))
            and (not pixel_format.lower().endswith("a"))
            and (pixel_format.lower() == "rgb24")
        )

        # Optional true GPU decode backend (no ffmpeg stdout pipe), only in auto
        # mode or when explicitly requested.
        force_true_gpu = backend in {"gpu", "cuda", "nvdec", "decord"}

        if force_true_gpu or is_auto:
            try:
                self.reader = _try_make_true_gpu_reader()
            except Exception:
                self.reader = None

        if self.reader is None:
            if (force_opencv or is_auto) and can_use_opencv:
                try:
                    self.reader = _try_make_opencv_reader()
                except Exception:
                    self.reader = _make_ffmpeg_reader()
            elif force_ffmpeg:
                self.reader = _make_ffmpeg_reader()
            elif force_true_gpu:
                # Explicit request but unavailable; be conservative.
                self.reader = _make_ffmpeg_reader()
            else:
                # Unknown backend value; be conservative.
                self.reader = _make_ffmpeg_reader()

        # Make some of the reader's attributes accessible from the clip
        self.duration = self.reader.duration
        self.end = self.reader.duration

        self.fps = self.reader.fps
        self.size = self.reader.size
        self.rotation = self.reader.rotation

        self.filename = filename

        # Internal ffmpeg fast-path metadata.
        #
        # If the clip remains a raw, untransformed VideoFileClip (optionally
        # subclipped), we can write it by calling ffmpeg directly on the source
        # file and avoid iterating frames in Python.
        #
        # Any visual transform/effect should clear these attributes.
        self._ffmpeg_source_filename = filename
        self._ffmpeg_source_start = 0.0
        self._ffmpeg_source_target_resolution = target_resolution
        self._ffmpeg_source_resize_algorithm = resize_algorithm

        if has_mask:
            self.frame_function = lambda t: self.reader.get_frame(t)[:, :, :3]

            def mask_frame_function(t):
                return self.reader.get_frame(t)[:, :, 3] / 255.0

            self.mask = VideoClip(
                is_mask=True, frame_function=mask_frame_function
            ).with_duration(self.duration)
            self.mask.fps = self.fps

        else:
            self.frame_function = lambda t: self.reader.get_frame(t)

        # Internal GPU frame function: if the reader can provide GPU frames,
        # expose it for the experimental GPU compositor/export path.
        if hasattr(self.reader, "get_frame_gpu"):
            try:
                self._gpu_frame_function = lambda t: self.reader.get_frame_gpu(t)
            except Exception:
                pass

        # Internal batch GPU decode hook.
        # This is only safe for the *raw* VideoFileClip and should not be relied
        # upon after arbitrary transform/effect chains.
        self._gpu_batch_safe = bool(hasattr(self.reader, "get_batch_gpu"))
        if self._gpu_batch_safe:
            try:
                self._gpu_frame_function_batch_by_index = (
                    lambda idxs: self.reader.get_batch_gpu(idxs)
                )
            except Exception:
                self._gpu_batch_safe = False

        # Make a reader for the audio, if any.
        if audio and self.reader.infos["audio_found"]:
            self.audio = AudioFileClip(
                filename,
                buffersize=audio_buffersize,
                fps=audio_fps,
                nbytes=audio_nbytes,
                audio_stream_index=audio_stream_index,
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
