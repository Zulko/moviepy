"""Implements VideoClip (base class for video clips) and its main subclasses:

- Animated clips:     VideoFileClip, ImageSequenceClip, BitmapClip
- Static image clips: ImageClip, ColorClip, TextClip,
"""

import copy as _copy
import os
import threading
from numbers import Real
from typing import TYPE_CHECKING, Callable, List, Union

import numpy as np
import proglog
from imageio.v2 import imread as imread_v2
from imageio.v3 import imwrite
from PIL import Image, ImageDraw, ImageFont

from moviepy.video.io.ffplay_previewer import ffplay_preview_video


if TYPE_CHECKING:
    from moviepy.Effect import Effect

from moviepy.Clip import Clip
from moviepy.decorators import (
    add_mask_if_none,
    apply_to_mask,
    convert_masks_to_RGB,
    convert_parameter_to_seconds,
    convert_path_to_string,
    outplace,
    requires_duration,
    requires_fps,
    use_clip_fps_by_default,
)
from moviepy.tools import compute_position, extensions_dict, find_extension
from moviepy.video.fx.Crop import Crop
from moviepy.video.fx.Resize import Resize
from moviepy.video.fx.Rotate import Rotate
from moviepy.video.io.ffmpeg_writer import ffmpeg_write_video
from moviepy.video.io.gif_writers import write_gif_with_imageio


class VideoClip(Clip):
    """Base class for video clips.

    See ``VideoFileClip``, ``ImageClip`` etc. for more user-friendly classes.


    Parameters
    ----------

    is_mask
      `True` if the clip is going to be used as a mask.

    duration
      Duration of the clip in seconds. If None we got a clip of infinite
      duration

    has_constant_size
      Define if clip size is constant or if it may vary with time. Default
      to True



    Attributes
    ----------

    size
      The size of the clip, (width,height), in pixels.

    w, h
      The width and height of the clip, in pixels.

    is_mask
      Boolean set to `True` if the clip is a mask.

    frame_function
      A function ``t-> frame at time t`` where ``frame`` is a
      w*h*3 RGB array.

    mask (default None)
      VideoClip mask attached to this clip. If mask is ``None``,
                The video clip is fully opaque.

    audio (default None)
      An AudioClip instance containing the audio of the video clip.

    pos
      A function ``t->(x,y)`` where ``x,y`` is the position
      of the clip when it is composed with other clips.
      See ``VideoClip.set_pos`` for more details

    relative_pos
      See variable ``pos``.

    layer
      Indicates which clip is rendered on top when two clips overlap in
      a CompositeVideoClip. The highest number is rendered on top.
      Default is 0.

    """

    def __init__(
        self, frame_function=None, is_mask=False, duration=None, has_constant_size=True
    ):
        super().__init__()
        self.mask = None
        self.audio = None
        self.pos = lambda t: (0, 0)
        self.relative_pos = False
        self.layer_index = 0
        if frame_function:
            self.frame_function = frame_function
            self.size = self.get_frame(0).shape[:2][::-1]
        self.is_mask = is_mask
        self.has_constant_size = has_constant_size
        if duration is not None:
            self.duration = duration
            self.end = duration

    @property
    def w(self):
        """Returns the width of the video."""
        return self.size[0]

    @property
    def h(self):
        """Returns the height of the video."""
        return self.size[1]

    @property
    def aspect_ratio(self):
        """Returns the aspect ratio of the video."""
        return self.w / float(self.h)

    @property
    @requires_duration
    @requires_fps
    def n_frames(self):
        """Returns the number of frames of the video."""
        return int(self.duration * self.fps)

    def __copy__(self):
        """Mixed copy of the clip.

        Returns a shallow copy of the clip whose mask and audio will
        be shallow copies of the clip's mask and audio if they exist.

        This method is intensively used to produce new clips every time
        there is an outplace transformation of the clip (clip.resize,
        clip.subclipped, etc.)

        Acts like a deepcopy except for the fact that readers and other
        possible unpickleables objects are not copied.
        """
        cls = self.__class__
        new_clip = cls.__new__(cls)
        for attr in self.__dict__:
            value = getattr(self, attr)
            if attr in ("mask", "audio"):
                value = _copy.copy(value)
            setattr(new_clip, attr, value)
        return new_clip

    copy = __copy__

    # ===============================================================
    # EXPORT OPERATIONS

    @convert_parameter_to_seconds(["t"])
    @convert_masks_to_RGB
    def save_frame(self, filename, t=0, with_mask=True):
        """Save a clip's frame to an image file.

        Saves the frame of clip corresponding to time ``t`` in ``filename``.
        ``t`` can be expressed in seconds (15.35), in (min, sec),
        in (hour, min, sec), or as a string: '01:03:05.35'.

        Parameters
        ----------

        filename : str
          Name of the file in which the frame will be stored.

        t : float or tuple or str, optional
          Moment of the frame to be saved. As default, the first frame will be
          saved.

        with_mask : bool, optional
          If is ``True`` the mask is saved in the alpha layer of the picture
          (only works with PNGs).
        """
        im = self.get_frame(t)
        if with_mask and self.mask is not None:
            mask = 255 * self.mask.get_frame(t)
            im = np.dstack([im, mask]).astype("uint8")
        else:
            im = im.astype("uint8")

        imwrite(filename, im)

    @requires_duration
    @use_clip_fps_by_default
    @convert_masks_to_RGB
    @convert_path_to_string(["filename", "temp_audiofile", "temp_audiofile_path"])
    def write_videofile(
        self,
        filename,
        fps=None,
        codec=None,
        bitrate=None,
        audio=True,
        audio_fps=44100,
        preset="medium",
        audio_nbytes=4,
        audio_codec=None,
        audio_bitrate=None,
        audio_bufsize=2000,
        temp_audiofile=None,
        temp_audiofile_path="",
        remove_temp=True,
        write_logfile=False,
        threads=None,
        ffmpeg_params=None,
        logger="bar",
        pixel_format=None,
    ):
        """Write the clip to a videofile.

        Parameters
        ----------

        filename
          Name of the video file to write in, as a string or a path-like object.
          The extension must correspond to the "codec" used (see below),
          or simply be '.avi' (which will work with any codec).

        fps
          Number of frames per second in the resulting video file. If None is
          provided, and the clip has an fps attribute, this fps will be used.

        codec
          Codec to use for image encoding. Can be any codec supported
          by ffmpeg. If the filename is has extension '.mp4', '.ogv', '.webm',
          the codec will be set accordingly, but you can still set it if you
          don't like the default. For other extensions, the output filename
          must be set accordingly.

          Some examples of codecs are:

          - ``'libx264'`` (default codec for file extension ``.mp4``)
            makes well-compressed videos (quality tunable using 'bitrate').
          - ``'mpeg4'`` (other codec for extension ``.mp4``) can be an alternative
            to ``'libx264'``, and produces higher quality videos by default.
          - ``'rawvideo'`` (use file extension ``.avi``) will produce
            a video of perfect quality, of possibly very huge size.
          - ``png`` (use file extension ``.avi``) will produce a video
            of perfect quality, of smaller size than with ``rawvideo``.
          - ``'libvorbis'`` (use file extension ``.ogv``) is a nice video
            format, which is completely free/ open source. However not
            everyone has the codecs installed by default on their machine.
          - ``'libvpx'`` (use file extension ``.webm``) is tiny a video
            format well indicated for web videos (with HTML5). Open source.

        audio
          Either ``True``, ``False``, or a file name.
          If ``True`` and the clip has an audio clip attached, this
          audio clip will be incorporated as a soundtrack in the movie.
          If ``audio`` is the name of an audio file, this audio file
          will be incorporated as a soundtrack in the movie.

        audio_fps
          frame rate to use when generating the sound.

        temp_audiofile
          the name of the temporary audiofile, as a string or path-like object,
          to be created and then used to write the complete video, if any.

        temp_audiofile_path
          the location that the temporary audiofile is placed, as a
          string or path-like object. Defaults to the current working directory.

        audio_codec
          Which audio codec should be used. Examples are 'libmp3lame'
          for '.mp3', 'libvorbis' for 'ogg', 'libfdk_aac':'m4a',
          'pcm_s16le' for 16-bit wav and 'pcm_s32le' for 32-bit wav.
          Default is 'libmp3lame', unless the video extension is 'ogv'
          or 'webm', at which case the default is 'libvorbis'.

        audio_bitrate
          Audio bitrate, given as a string like '50k', '500k', '3000k'.
          Will determine the size/quality of audio in the output file.
          Note that it mainly an indicative goal, the bitrate won't
          necessarily be the this in the final file.

        preset
          Sets the time that FFMPEG will spend optimizing the compression.
          Choices are: ultrafast, superfast, veryfast, faster, fast, medium,
          slow, slower, veryslow, placebo. Note that this does not impact
          the quality of the video, only the size of the video file. So
          choose ultrafast when you are in a hurry and file size does not
          matter.

        threads
          Number of threads to use for ffmpeg. Can speed up the writing of
          the video on multicore computers.

        ffmpeg_params
          Any additional ffmpeg parameters you would like to pass, as a list
          of terms, like ['-option1', 'value1', '-option2', 'value2'].

        write_logfile
          If true, will write log files for the audio and the video.
          These will be files ending with '.log' with the name of the
          output file in them.

        logger
          Either ``"bar"`` for progress bar or ``None`` or any Proglog logger.

        pixel_format
          Pixel format for the output video file.

        Examples
        --------

        .. code:: python

            from moviepy import VideoFileClip
            clip = VideoFileClip("myvideo.mp4").subclipped(100,120)
            clip.write_videofile("my_new_video.mp4")
            clip.close()

        """
        name, ext = os.path.splitext(os.path.basename(filename))
        ext = ext[1:].lower()
        logger = proglog.default_bar_logger(logger)

        if codec is None:
            try:
                codec = extensions_dict[ext]["codec"][0]
            except KeyError:
                raise ValueError(
                    "MoviePy couldn't find the codec associated "
                    "with the filename. Provide the 'codec' "
                    "parameter in write_videofile."
                )

        if audio_codec is None:
            if ext in ["ogv", "webm"]:
                audio_codec = "libvorbis"
            else:
                audio_codec = "libmp3lame"
        elif audio_codec == "raw16":
            audio_codec = "pcm_s16le"
        elif audio_codec == "raw32":
            audio_codec = "pcm_s32le"

        audiofile = audio if isinstance(audio, str) else None
        make_audio = (
            (audiofile is None) and (audio is True) and (self.audio is not None)
        )

        if make_audio and temp_audiofile:
            # The audio will be the clip's audio
            audiofile = temp_audiofile
        elif make_audio:
            audio_ext = find_extension(audio_codec)
            audiofile = os.path.join(
                temp_audiofile_path,
                name + Clip._TEMP_FILES_PREFIX + "wvf_snd.%s" % audio_ext,
            )

        # enough cpu for multiprocessing ? USELESS RIGHT NOW, WILL COME AGAIN
        # enough_cpu = (multiprocessing.cpu_count() > 1)
        logger(message="MoviePy - Building video %s." % filename)
        if make_audio:
            self.audio.write_audiofile(
                audiofile,
                audio_fps,
                audio_nbytes,
                audio_bufsize,
                audio_codec,
                bitrate=audio_bitrate,
                write_logfile=write_logfile,
                logger=logger,
            )
            # The audio is already encoded,
            # so there is no need to encode it during video export
            audio_codec = "copy"

        ffmpeg_write_video(
            self,
            filename,
            fps,
            codec,
            bitrate=bitrate,
            preset=preset,
            write_logfile=write_logfile,
            audiofile=audiofile,
            audio_codec=audio_codec,
            threads=threads,
            ffmpeg_params=ffmpeg_params,
            logger=logger,
            pixel_format=pixel_format,
        )

        if remove_temp and make_audio:
            if os.path.exists(audiofile):
                os.remove(audiofile)
        logger(message="MoviePy - video ready %s" % filename)

    @requires_duration
    @use_clip_fps_by_default
    @convert_masks_to_RGB
    def write_images_sequence(
        self, name_format, fps=None, with_mask=True, logger="bar"
    ):
        """Writes the videoclip to a sequence of image files.

        Parameters
        ----------

        name_format
          A filename specifying the numerotation format and extension
          of the pictures. For instance "frame%03d.png" for filenames
          indexed with 3 digits and PNG format. Also possible:
          "some_folder/frame%04d.jpeg", etc.

        fps
          Number of frames per second to consider when writing the
          clip. If not specified, the clip's ``fps`` attribute will
          be used if it has one.

        with_mask
          will save the clip's mask (if any) as an alpha canal (PNGs only).

        logger
          Either ``"bar"`` for progress bar or ``None`` or any Proglog logger.


        Returns
        -------

        names_list
          A list of all the files generated.

        Notes
        -----

        The resulting image sequence can be read using e.g. the class
        ``ImageSequenceClip``.

        """
        logger = proglog.default_bar_logger(logger)
        # Fails on GitHub macos CI
        # logger(message="MoviePy - Writing frames %s." % name_format)

        timings = np.arange(0, self.duration, 1.0 / fps)

        filenames = []
        for i, t in logger.iter_bar(t=list(enumerate(timings))):
            name = name_format % i
            filenames.append(name)
            self.save_frame(name, t, with_mask=with_mask)
        # logger(message="MoviePy - Done writing frames %s." % name_format)

        return filenames

    @requires_duration
    @convert_masks_to_RGB
    @convert_path_to_string("filename")
    def write_gif(
        self,
        filename,
        fps=None,
        loop=0,
        logger="bar",
    ):
        """Write the VideoClip to a GIF file.

        Converts a VideoClip into an animated GIF using imageio

        Parameters
        ----------

        filename
          Name of the resulting gif file, as a string or a path-like object.

        fps
          Number of frames per second (see note below). If it
          isn't provided, then the function will look for the clip's
          ``fps`` attribute (VideoFileClip, for instance, have one).

        loop : int, optional
          Repeat the clip using ``loop`` iterations in the resulting GIF.

        progress_bar
          If True, displays a progress bar


        Notes
        -----

        The gif will be playing the clip in real time (you can
        only change the frame rate). If you want the gif to be played
        slower than the clip you will use

        .. code:: python

            # slow down clip 50% and make it a gif
            myClip.multiply_speed(0.5).to_gif('myClip.gif')

        """
        # A little sketchy at the moment, maybe move all that in write_gif,
        #  refactor a little... we will see.

        write_gif_with_imageio(
            self,
            filename,
            fps=fps,
            loop=loop,
            logger=logger,
        )

    # ===============================================================
    # PREVIEW OPERATIONS

    @convert_masks_to_RGB
    @convert_parameter_to_seconds(["t"])
    def show(self, t=0, with_mask=True):
        """Splashes the frame of clip corresponding to time ``t``.

        Parameters
        ----------

        t : float or tuple or str, optional
        Time in seconds of the frame to display.

        with_mask : bool, optional
        ``False`` if the clip has a mask but you want to see the clip without
        the mask.

        Examples
        --------

        .. code:: python

            from moviepy import *

            clip = VideoFileClip("media/chaplin.mp4")
            clip.show(t=4)
        """
        clip = self.copy()

        # Warning : Comment to fix a bug on preview for compositevideoclip
        # it broke compositevideoclip and it does nothing on normal clip with alpha

        # if with_mask and (self.mask is not None):
        #   # Hate it, but cannot figure a better way with python awful circular
        #   # dependency
        #   from mpy.video.compositing.CompositeVideoClip import CompositeVideoClip
        #   clip = CompositeVideoClip([self.with_position((0, 0))])

        frame = clip.get_frame(t)
        pil_img = Image.fromarray(frame.astype("uint8"))

        pil_img.show()

    @requires_duration
    @convert_masks_to_RGB
    def preview(
        self, fps=15, audio=True, audio_fps=22050, audio_buffersize=3000, audio_nbytes=2
    ):
        """Displays the clip in a window, at the given frames per second.

        It will avoid that the clip be played faster than normal, but it
        cannot avoid the clip to be played slower than normal if the computations
        are complex. In this case, try reducing the ``fps``.

        Parameters
        ----------

        fps : int, optional
        Number of frames per seconds in the displayed video. Default to ``15``.

        audio : bool, optional
        ``True`` (default) if you want the clip's audio be played during
        the preview.

        audio_fps : int, optional
        The frames per second to use when generating the audio sound.

        audio_buffersize : int, optional
        The sized of the buffer used generating the audio sound.

        audio_nbytes : int, optional
        The number of bytes used generating the audio sound.

        Examples
        --------

        .. code:: python

            from moviepy import *
            clip = VideoFileClip("media/chaplin.mp4")
            clip.preview(fps=10, audio=False)
        """
        audio = audio and (self.audio is not None)
        audio_flag = None
        video_flag = None

        if audio:
            # the sound will be played in parallel. We are not
            # parralellizing it on different CPUs because it seems that
            # ffplay use several cpus.

            # two synchro-flags to tell whether audio and video are ready
            video_flag = threading.Event()
            audio_flag = threading.Event()
            # launch the thread
            audiothread = threading.Thread(
                target=self.audio.audiopreview,
                args=(
                    audio_fps,
                    audio_buffersize,
                    audio_nbytes,
                    audio_flag,
                    video_flag,
                ),
            )
            audiothread.start()

        # passthrough to ffmpeg, passing flag for ffmpeg to set
        ffplay_preview_video(
            clip=self, fps=fps, audio_flag=audio_flag, video_flag=video_flag
        )

    # -----------------------------------------------------------------
    # F I L T E R I N G

    def with_effects_on_subclip(
        self, effects: List["Effect"], start_time=0, end_time=None, **kwargs
    ):
        """Apply a transformation to a part of the clip.

        Returns a new clip in which the function ``fun`` (clip->clip)
        has been applied to the subclip between times `start_time` and `end_time`
        (in seconds).

        Examples
        --------

        .. code:: python

            # The scene between times t=3s and t=6s in ``clip`` will be
            # be played twice slower in ``new_clip``
            new_clip = clip.with_sub_effect(MultiplySpeed(0.5), 3, 6)

        """
        left = None if (start_time == 0) else self.subclipped(0, start_time)
        center = self.subclipped(start_time, end_time).with_effects(effects, **kwargs)
        right = None if (end_time is None) else self.subclipped(start_time=end_time)

        clips = [clip for clip in [left, center, right] if clip is not None]

        # beurk, have to find other solution
        from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips

        return concatenate_videoclips(clips).with_start(self.start)

    # IMAGE FILTERS

    def image_transform(self, image_func, apply_to=None):
        """Modifies the images of a clip by replacing the frame `get_frame(t)` by
        another frame,  `image_func(get_frame(t))`.
        """
        apply_to = apply_to or []
        return self.transform(lambda get_frame, t: image_func(get_frame(t)), apply_to)

    # --------------------------------------------------------------
    # C O M P O S I T I N G

    def fill_array(self, pre_array, shape=(0, 0)):
        """Fills an array to match the specified shape.

        If the `pre_array` is smaller than the desired shape, the missing rows
        or columns are added with ones to the bottom or right, respectively,
        until the shape matches. If the `pre_array` is larger than the desired
        shape, the excess rows or columns are cropped from the bottom or right,
        respectively, until the shape matches.

        The resulting array with the filled shape is returned.

        Parameters
        ----------
        pre_array (numpy.ndarray)
          The original array to be filled.

        shape (tuple)
          The desired shape of the resulting array.
        """
        pre_shape = pre_array.shape
        dx = shape[0] - pre_shape[0]
        dy = shape[1] - pre_shape[1]
        post_array = pre_array
        if dx < 0:
            post_array = pre_array[: shape[0]]
        elif dx > 0:
            x_1 = [[[1, 1, 1]] * pre_shape[1]] * dx
            post_array = np.vstack((pre_array, x_1))
        if dy < 0:
            post_array = post_array[:, : shape[1]]
        elif dy > 0:
            x_1 = [[[1, 1, 1]] * dy] * post_array.shape[0]
            post_array = np.hstack((post_array, x_1))
        return post_array

    def compose_on(self, background: Image.Image, t) -> Image.Image:
        """Returns the result of the clip's frame at time `t` on top
        on the given `picture`, the position of the clip being given
        by the clip's ``pos`` attribute. Meant for compositing.

        If the clip/backgrounds have transparency the transparency will
        be accounted for.

        The return is a Pillow Image

        Parameters
        ----------
        backrgound (Image)
          The background image to apply current clip on top of
          if the background image is transparent it must be given as a RGBA image

        t
          The time of clip to apply on top of clip

        Return
        """
        ct = t - self.start  # clip time

        # GET IMAGE AND MASK IF ANY
        clip_frame = self.get_frame(ct).astype("uint8")
        clip_img = Image.fromarray(clip_frame)

        if self.mask is not None:
            clip_mask = (self.mask.get_frame(ct) * 255).astype("uint8")
            clip_mask_img = Image.fromarray(clip_mask).convert("L")

            # Resize clip_mask_img to match clip_img, always use top left corner
            if clip_mask_img.size != clip_img.size:
                mask_width, mask_height = clip_mask_img.size
                img_width, img_height = clip_img.size

                if mask_width > img_width or mask_height > img_height:
                    # Crop mask if it is larger
                    clip_mask_img = clip_mask_img.crop((0, 0, img_width, img_height))
                else:
                    # Fill mask with 0 if it is smaller
                    new_mask = Image.new("L", (img_width, img_height), 0)
                    new_mask.paste(clip_mask_img, (0, 0))
                    clip_mask_img = new_mask

            clip_img = clip_img.convert("RGBA")
            clip_img.putalpha(clip_mask_img)

        # SET POSITION
        pos = self.pos(ct)
        pos = compute_position(clip_img.size, background.size, pos, self.relative_pos)

        # If neither background nor clip have alpha layer (check if mode end
        # with A), we can juste use pillow paste
        if clip_img.mode[-1] != "A" and background.mode[-1] != "A":
            background.paste(clip_img, pos)
            return background

        # For images with transparency we must use pillow alpha composite
        # instead of a simple paste, because pillow paste dont work nicely
        # with alpha compositing
        if background.mode[-1] != "A":
            background = background.convert("RGBA")

        if clip_img.mode[-1] != "A":
            clip_img = clip_img.convert("RGBA")

        # We need both image to do the same size for alpha compositing in pillow
        # so we must start by making a fully transparent canvas of background's
        # size and paste our clip img into it in position pos, only then can we
        # composite this canvas on top of background
        canvas = Image.new("RGBA", (background.width, background.height), (0, 0, 0, 0))
        canvas.paste(clip_img, pos)
        result = Image.alpha_composite(background, canvas)
        return result

    def compose_mask(self, background_mask: np.ndarray, t: float) -> np.ndarray:
        """Returns the result of the clip's mask at time `t` composited
        on the given `background_mask`, the position of the clip being given
        by the clip's ``pos`` attribute. Meant for compositing.

        (warning: only use this function to blit two masks together, never images)

        Parameters
        ----------
        background_mask:
          The underlying mask onto which the clip mask will be composed.

        t:
          The time position in the clip at which to extract the mask.
        """
        ct = t - self.start  # clip time
        clip_mask = self.get_frame(ct).astype("float")

        # numpy shape is H*W not W*H
        bg_h, bg_w = background_mask.shape
        clip_h, clip_w = clip_mask.shape

        # SET POSITION
        pos = self.pos(ct)
        pos = compute_position((clip_w, clip_h), (bg_w, bg_h), pos, self.relative_pos)

        # ALPHA COMPOSITING
        # Determine the base_mask region to merge size
        x_start = int(max(pos[0], 0))  # Dont go under 0 left
        x_end = int(min(pos[0] + clip_w, bg_w))  # Dont go over base_mask width
        y_start = int(max(pos[1], 0))  # Dont go under 0 top
        y_end = int(min(pos[1] + clip_h, bg_h))  # Dont go over base_mask height

        # Determine the clip_mask region to overlapp
        # Dont go under 0 for horizontal, if we have negative margin of X px start at X
        # And dont go over clip width
        clip_x_start = int(max(0, -pos[0]))
        clip_x_end = int(clip_x_start + min((x_end - x_start), (clip_w - clip_x_start)))
        # same for vertical
        clip_y_start = int(max(0, -pos[1]))
        clip_y_end = int(clip_y_start + min((y_end - y_start), (clip_h - clip_y_start)))

        # Blend the overlapping regions
        # The calculus is base_opacity + clip_opacity * (1 - base_opacity)
        # this ensure that masks are drawn in the right order and
        # the contribution of each mask is proportional to their transparency
        #
        # Note :
        # Thinking in transparency is hard, as we tend to think
        # that 50% opaque + 40% opaque = 90% opacity, when it really its 70%
        # It's a lot easier to think in terms of "passing light"
        # Consider I emit 100 photons, and my first layer is 50% opaque, meaning it
        # will "stop" 50% of the photons, I'll have 50 photons left
        # now my second layer is blocking 40% of thoses 50 photons left
        # blocking 50 * 0.4 = 20 photons, and leaving me with only 30 photons
        # So, by adding two layer of 50% and 40% opacity my finaly opacity is only
        # of (100-30)*100 = 70% opacity !
        background_mask[y_start:y_end, x_start:x_end] = background_mask[
            y_start:y_end, x_start:x_end
        ] + clip_mask[clip_y_start:clip_y_end, clip_x_start:clip_x_end] * (
            1 - background_mask[y_start:y_end, x_start:x_end]
        )

        return background_mask

    def with_background_color(self, size=None, color=(0, 0, 0), pos=None, opacity=None):
        """Place the clip on a colored background.

        Returns a clip made of the current clip overlaid on a color
        clip of a possibly bigger size. Can serve to flatten transparent
        clips.

        Parameters
        ----------

        size
          Size (width, height) in pixels of the final clip.
          By default it will be the size of the current clip.

        color
          Background color of the final clip ([R,G,B]).

        pos
          Position of the clip in the final clip. 'center' is the default

        opacity
          Parameter in 0..1 indicating the opacity of the colored
          background.
        """
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

        if size is None:
            size = self.size
        if pos is None:
            pos = "center"

        if opacity is not None:
            colorclip = ColorClip(
                size, color=color, duration=self.duration
            ).with_opacity(opacity)
            result = CompositeVideoClip([colorclip, self.with_position(pos)])
        else:
            result = CompositeVideoClip(
                [self.with_position(pos)], size=size, bg_color=color
            )

        if (
            isinstance(self, ImageClip)
            and (not hasattr(pos, "__call__"))
            and ((self.mask is None) or isinstance(self.mask, ImageClip))
        ):
            new_result = result.to_ImageClip()
            if result.mask is not None:
                new_result.mask = result.mask.to_ImageClip()
            return new_result.with_duration(result.duration)

        return result

    @outplace
    def with_updated_frame_function(
        self, frame_function: Callable[[float], np.ndarray]
    ):
        """Change the clip's ``get_frame``.

        Returns a copy of the VideoClip instance, with the frame_function
        attribute set to `mf`.
        """
        self.frame_function = frame_function
        self.size = self.get_frame(0).shape[:2][::-1]

    @outplace
    def with_audio(self, audioclip):
        """Attach an AudioClip to the VideoClip.

        Returns a copy of the VideoClip instance, with the `audio`
        attribute set to ``audio``, which must be an AudioClip instance.
        """
        self.audio = audioclip

    @outplace
    def with_mask(self, mask: Union["VideoClip", str] = "auto"):
        """
        Set the clip's mask.

        Returns a copy of the VideoClip with the mask attribute set to
        ``mask``, which must be a greyscale (values in 0-1) VideoClip.

        Parameters
        ----------
        mask : Union["VideoClip", str], optional
            The mask to apply to the clip.
            If set to "auto", a default mask will be generated:
            - If the clip has a constant size, a solid mask with a value of 1.0
            will be created.
            - Otherwise, a dynamic solid mask will be created based on the frame size.
        """
        if mask == "auto":
            if self.has_constant_size:
                mask = ColorClip(self.size, 1.0, is_mask=True)
            else:

                def frame_function(t):
                    return np.ones(self.get_frame(t).shape[:2], dtype=float)

                mask = VideoClip(is_mask=True, frame_function=frame_function)
        self.mask = mask

    @outplace
    def without_mask(self):
        """Remove the clip's mask."""
        self.mask = None

    @add_mask_if_none
    @outplace
    def with_opacity(self, opacity):
        """Set the opacity/transparency level of the clip.

        Returns a semi-transparent copy of the clip where the mask is
        multiplied by ``op`` (any float, normally between 0 and 1).
        """
        self.mask = self.mask.image_transform(lambda pic: opacity * pic)

    @apply_to_mask
    @outplace
    def with_position(self, pos, relative=False):
        """Set the clip's position in compositions.

        Sets the position that the clip will have when included
        in compositions. The argument ``pos`` can be either a couple
        ``(x,y)`` or a function ``t-> (x,y)``. `x` and `y` mark the
        location of the top left corner of the clip, and can be
        of several types.

        Examples
        --------

        .. code:: python

            clip.with_position((45,150)) # x=45, y=150

            # clip horizontally centered, at the top of the picture
            clip.with_position(("center","top"))

            # clip is at 40% of the width, 70% of the height:
            clip.with_position((0.4,0.7), relative=True)

            # clip's position is horizontally centered, and moving up !
            clip.with_position(lambda t: ('center', 50+t))

        """
        self.relative_pos = relative
        if hasattr(pos, "__call__"):
            self.pos = pos
        else:
            self.pos = lambda t: pos

    @apply_to_mask
    @outplace
    def with_layer_index(self, index):
        """Set the clip's layer in compositions. Clips with a greater ``layer``
        attribute will be displayed on top of others.

        Note: Only has effect when the clip is used in a CompositeVideoClip.
        """
        self.layer_index = index

    def resized(self, new_size=None, height=None, width=None, apply_to_mask=True):
        """Returns a video clip that is a resized version of the clip.
        For info on the parameters, please see ``vfx.Resize``
        """
        return self.with_effects(
            [
                Resize(
                    new_size=new_size,
                    height=height,
                    width=width,
                    apply_to_mask=apply_to_mask,
                )
            ]
        )

    def rotated(
        self,
        angle: float,
        unit: str = "deg",
        resample: str = "bicubic",
        expand: bool = False,
        center: tuple = None,
        translate: tuple = None,
        bg_color: tuple = None,
    ):
        """Rotates the specified clip by ``angle`` degrees (or radians) anticlockwise
        If the angle is not a multiple of 90 (degrees) or ``center``, ``translate``,
        and ``bg_color`` are not ``None``.
        For info on the parameters, please see ``vfx.Rotate``
        """
        return self.with_effects(
            [
                Rotate(
                    angle=angle,
                    unit=unit,
                    resample=resample,
                    expand=expand,
                    center=center,
                    translate=translate,
                    bg_color=bg_color,
                )
            ]
        )

    def cropped(
        self,
        x1: int = None,
        y1: int = None,
        x2: int = None,
        y2: int = None,
        width: int = None,
        height: int = None,
        x_center: int = None,
        y_center: int = None,
    ):
        """Returns a new clip in which just a rectangular subregion of the
        original clip is conserved. x1,y1 indicates the top left corner and
        x2,y2 is the lower right corner of the cropped region.
        All coordinates are in pixels. Float numbers are accepted.
        For info on the parameters, please see ``vfx.Crop``
        """
        return self.with_effects(
            [
                Crop(
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    width=width,
                    height=height,
                    x_center=x_center,
                    y_center=y_center,
                )
            ]
        )

    # --------------------------------------------------------------
    # CONVERSIONS TO OTHER TYPES

    @convert_parameter_to_seconds(["t"])
    def to_ImageClip(self, t=0, with_mask=True, duration=None):
        """
        Returns an ImageClip made out of the clip's frame at time ``t``,
        which can be expressed in seconds (15.35), in (min, sec),
        in (hour, min, sec), or as a string: '01:03:05.35'.
        """
        new_clip = ImageClip(self.get_frame(t), is_mask=self.is_mask, duration=duration)
        if with_mask and self.mask is not None:
            new_clip.mask = self.mask.to_ImageClip(t)
        return new_clip

    def to_mask(self, canal=0):
        """Return a mask a video clip made from the clip."""
        if self.is_mask:
            return self
        else:
            new_clip = self.image_transform(lambda pic: 1.0 * pic[:, :, canal] / 255)
            new_clip.is_mask = True
            return new_clip

    def to_RGB(self):
        """Return a non-mask video clip made from the mask video clip."""
        if self.is_mask:
            new_clip = self.image_transform(
                lambda pic: np.dstack(3 * [255 * pic]).astype("uint8")
            )
            new_clip.is_mask = False
            return new_clip
        else:
            return self

    # ----------------------------------------------------------------
    # Audio

    @outplace
    def without_audio(self):
        """Remove the clip's audio.

        Return a copy of the clip with audio set to None.
        """
        self.audio = None

    def __add__(self, other):
        if isinstance(other, VideoClip):
            from moviepy.video.compositing.CompositeVideoClip import (
                concatenate_videoclips,
            )

            method = "chain" if self.size == other.size else "compose"
            return concatenate_videoclips([self, other], method=method)
        return super(VideoClip, self).__add__(other)

    def __or__(self, other):
        """
        Implement the or (self | other) to produce a video with self and other
        placed side by side horizontally.
        """
        if isinstance(other, VideoClip):
            from moviepy.video.compositing.CompositeVideoClip import clips_array

            return clips_array([[self, other]])
        return super(VideoClip, self).__or__(other)

    def __truediv__(self, other):
        """
        Implement division (self / other) to produce a video with self
        placed on top of other.
        """
        if isinstance(other, VideoClip):
            from moviepy.video.compositing.CompositeVideoClip import clips_array

            return clips_array([[self], [other]])
        return super(VideoClip, self).__or__(other)

    def __matmul__(self, n):
        """
        Implement matrice multiplication (self @ other) to rotate a video
        by other degrees
        """
        if not isinstance(n, Real):
            return NotImplemented

        from moviepy.video.fx.Rotate import Rotate

        return self.with_effects([Rotate(n)])

    def __and__(self, mask):
        """
        Implement the and (self & other) to produce a video with other
        used as a mask for self.
        """
        return self.with_mask(mask)


class DataVideoClip(VideoClip):
    """
    Class of video clips whose successive frames are functions
    of successive datasets

    Parameters
    ----------
    data
      A list of datasets, each dataset being used for one frame of the clip

    data_to_frame
      A function d -> video frame, where d is one element of the list `data`

    fps
      Number of frames per second in the animation
    """

    def __init__(self, data, data_to_frame, fps, is_mask=False, has_constant_size=True):
        self.data = data
        self.data_to_frame = data_to_frame
        self.fps = fps

        def frame_function(t):
            return self.data_to_frame(self.data[int(self.fps * t)])

        VideoClip.__init__(
            self,
            frame_function,
            is_mask=is_mask,
            duration=1.0 * len(data) / fps,
            has_constant_size=has_constant_size,
        )


class UpdatedVideoClip(VideoClip):
    """
    Class of clips whose frame_function requires some objects to
    be updated. Particularly practical in science where some
    algorithm needs to make some steps before a new frame can
    be generated.

    UpdatedVideoClips have the following frame_function:

    .. code:: python

        def frame_function(t):
            while self.world.clip_t < t:
                world.update() # updates, and increases world.clip_t
            return world.to_frame()

    Parameters
    ----------

    world
      An object with the following attributes:
      - world.clip_t: the clip's time corresponding to the world's state.
      - world.update() : update the world's state, (including increasing
      world.clip_t of one time step).
      - world.to_frame() : renders a frame depending on the world's state.

    is_mask
      True if the clip is a WxH mask with values in 0-1

    duration
      Duration of the clip, in seconds

    """

    def __init__(self, world, is_mask=False, duration=None):
        self.world = world

        def frame_function(t):
            while self.world.clip_t < t:
                world.update()
            return world.to_frame()

        VideoClip.__init__(
            self, frame_function=frame_function, is_mask=is_mask, duration=duration
        )


"""---------------------------------------------------------------------

    ImageClip (base class for all 'static clips') and its subclasses
    ColorClip and TextClip.
    I would have liked to put these in a separate file but Python is bad
    at cyclic imports.

---------------------------------------------------------------------"""


class ImageClip(VideoClip):
    """Class for non-moving VideoClips.

    A video clip originating from a picture. This clip will simply
    display the given picture at all times.

    Examples
    --------

    >>> clip = ImageClip("myHouse.jpeg")
    >>> clip = ImageClip( someArray ) # a Numpy array represent

    Parameters
    ----------

    img
      Any picture file (png, tiff, jpeg, etc.) as a string or a path-like object,
      or any array representing an RGB image (for instance a frame from a VideoClip).

    is_mask
      Set this parameter to `True` if the clip is a mask.

    transparent
      Set this parameter to `True` (default) if you want the alpha layer
      of the picture (if it exists) to be used as a mask.

    Attributes
    ----------

    img
      Array representing the image of the clip.

    """

    def __init__(
        self, img, is_mask=False, transparent=True, fromalpha=False, duration=None
    ):
        VideoClip.__init__(self, is_mask=is_mask, duration=duration)

        if not isinstance(img, np.ndarray):
            # img is a string or path-like object, so read it in from disk
            img = imread_v2(img)  # We use v2 imread cause v3 fail with gif

        if len(img.shape) == 3:  # img is (now) a RGB(a) numpy array
            if img.shape[2] == 4:
                if fromalpha:
                    img = 1.0 * img[:, :, 3] / 255
                elif is_mask:
                    img = 1.0 * img[:, :, 0] / 255
                elif transparent:
                    self.mask = ImageClip(1.0 * img[:, :, 3] / 255, is_mask=True)
                    img = img[:, :, :3]
            elif is_mask:
                img = 1.0 * img[:, :, 0] / 255

        # if the image was just a 2D mask, it should arrive here
        # unchanged
        self.frame_function = lambda t: img
        self.size = img.shape[:2][::-1]
        self.img = img

    def transform(self, func, apply_to=None, keep_duration=True):
        """General transformation filter.

        Equivalent to VideoClip.transform. The result is no more an
        ImageClip, it has the class VideoClip (since it may be animated)
        """
        if apply_to is None:
            apply_to = []
        # When we use transform on an image clip it may become animated.
        # Therefore the result is not an ImageClip, just a VideoClip.
        new_clip = VideoClip.transform(
            self, func, apply_to=apply_to, keep_duration=keep_duration
        )
        new_clip.__class__ = VideoClip
        return new_clip

    @outplace
    def image_transform(self, image_func, apply_to=None):
        """Image-transformation filter.

        Does the same as VideoClip.image_transform, but for ImageClip the
        transformed clip is computed once and for all at the beginning,
        and not for each 'frame'.
        """
        if apply_to is None:
            apply_to = []
        arr = image_func(self.get_frame(0))
        self.size = arr.shape[:2][::-1]
        self.frame_function = lambda t: arr
        self.img = arr

        for attr in apply_to:
            a = getattr(self, attr, None)
            if a is not None:
                new_a = a.image_transform(image_func)
                setattr(self, attr, new_a)

    @outplace
    def time_transform(self, time_func, apply_to=None, keep_duration=False):
        """Time-transformation filter.

        Applies a transformation to the clip's timeline
        (see Clip.time_transform).

        This method does nothing for ImageClips (but it may affect their
        masks or their audios). The result is still an ImageClip.
        """
        if apply_to is None:
            apply_to = ["mask", "audio"]
        for attr in apply_to:
            a = getattr(self, attr, None)
            if a is not None:
                new_a = a.time_transform(time_func)
                setattr(self, attr, new_a)


class ColorClip(ImageClip):
    """An ImageClip showing just one color.

    Parameters
    ----------

    size
      Size tuple (width, height) in pixels of the clip.

    color
      If argument ``is_mask`` is False, ``color`` indicates
      the color in RGB of the clip (default is black). If `is_mask``
      is True, ``color`` must be  a float between 0 and 1 (default is 1)

    is_mask
      Set to true if the clip will be used as a mask.

    """

    def __init__(self, size, color=None, is_mask=False, duration=None):
        w, h = size

        if is_mask:
            shape = (h, w)
            if color is None:
                color = 0
            elif not np.isscalar(color):
                raise Exception("Color has to be a scalar when mask is true")
        else:
            if color is None:
                color = (0, 0, 0)
            elif not hasattr(color, "__getitem__"):
                raise Exception("Color has to contain RGB of the clip")
            elif isinstance(color, str):
                raise Exception(
                    "Color cannot be string. Color has to contain RGB of the clip"
                )
            shape = (h, w, len(color))

        super().__init__(
            np.tile(color, w * h).reshape(shape), is_mask=is_mask, duration=duration
        )


class TextClip(ImageClip):
    """Class for autogenerated text clips.

    Creates an ImageClip originating from a script-generated text image.

    Parameters
    ----------

    font
      Path to the font to use. Must be an OpenType font. If set to None
      (default) will use Pillow default font

    text
      A string of the text to write. Can be replaced by argument
      ``filename``.

    filename
      The name of a file in which there is the text to write,
      as a string or a path-like object.
      Can be provided instead of argument ``text``

    font_size
      Font size in point. Can be auto-set if method='caption',
      or if method='label' and size is set.

    size
      Size of the picture in pixels. Can be auto-set if
      method='label' and font_size is set, but mandatory if method='caption'.
      the height can be None for caption if font_size is defined,
      it will then be auto-determined.

    margin
      Margin to be added arround the text as a tuple of two (symmetrical) or
      four (asymmetrical). Either ``(horizontal, vertical)`` or
      ``(left, top, right, bottom)``. By default no margin (None, None).
      This is especially usefull for auto-compute size to give the text some
      extra room.

    color
      Color of the text. Default to "black". Can be
      a RGB (or RGBA if transparent = ``True``) ``tuple``, a color name, or an
      hexadecimal notation.

    bg_color
      Color of the background. Default to None for no background. Can be
      a RGB (or RGBA if transparent = ``True``) ``tuple``, a color name, or an
      hexadecimal notation.

    stroke_color
      Color of the stroke (=contour line) of the text. If ``None``,
      there will be no stroke.

    stroke_width
      Width of the stroke, in pixels. Must be an int.

    method
      Either :
        - 'label' (default), the picture will be autosized so as to fit the text
          either by auto-computing font size if width is provided or auto-computing
          width and eight if font size is defined

        - 'caption' the text will be drawn in a picture with fixed size provided
          with the ``size`` argument. The text will be wrapped automagically,
          either by auto-computing font size if width and height are provided or adding
          line break when necesarry if font size is defined

    text_align
      center | left | right. Text align similar to css. Default to ``left``.

    horizontal_align
      center | left | right. Define horizontal align of text bloc in image.
      Default to ``center``.

    vertical_align
      center | top | bottom. Define vertical align of text bloc in image.
      Default to ``center``.

    interline
      Interline spacing. Default to ``4``.

    transparent
      ``True`` (default) if you want to take into account the
      transparency in the image.

    duration
        Duration of the clip

    .. note::

      ** About final TextClip size **

      The final TextClip size will be of the absolute maximum height possible
      for the font and the number of line. It specifically mean that the final
      height might be a bit bigger than the real text height, i.e, absolute
      bottom pixel of text - absolute top pixel of text.
      This is because in a font, some letter go above standard top line (e.g
      letters with accents), and bellow standard baseline (e.g letters such as
      p, y, g).

      This notion is knowned under the name ascent and descent meaning the
      highest and lowest pixel above and below baseline

      If your first line dont have an "accent character" and your last line
      dont have a "descent character", you'll have some "fat" arround
    """

    @convert_path_to_string("filename")
    def __init__(
        self,
        font=None,
        text=None,
        filename=None,
        font_size=None,
        size=(None, None),
        margin=(None, None),
        color="black",
        bg_color=None,
        stroke_color=None,
        stroke_width=0,
        method="label",
        text_align="left",
        horizontal_align="center",
        vertical_align="center",
        interline=4,
        transparent=True,
        duration=None,
    ):
        if font is not None:
            try:
                _ = ImageFont.truetype(font)
            except Exception as e:
                raise ValueError(
                    "Invalid font {}, pillow failed to use it with error {}".format(
                        font, e
                    )
                )

        if filename:
            with open(filename, "r") as file:
                text = file.read().rstrip()  # Remove newline at end

        if text is None:
            raise ValueError("No text nor filename provided")

        if method not in ["caption", "label"]:
            raise ValueError("Method must be either `caption` or `label`.")

        # Compute the margin and apply it
        if len(margin) == 2:
            left_margin = right_margin = int(margin[0] or 0)
            top_margin = bottom_margin = int(margin[1] or 0)
        elif len(margin) == 4:
            left_margin = int(margin[0] or 0)
            top_margin = int(margin[1] or 0)
            right_margin = int(margin[2] or 0)
            bottom_margin = int(margin[3] or 0)
        else:
            raise ValueError("Margin must be a tuple of either 2 or 4 elements.")

        # Compute all img and text sizes if some are missing
        img_width, img_height = size

        if method == "caption":
            if img_width is None:
                raise ValueError("Size is mandatory when method is caption")

            if img_height is None and font_size is None:
                raise ValueError(
                    "Height is mandatory when method is caption and font size is None"
                )

            if font_size is None:
                font_size = self.__find_optimum_font_size(
                    text=text,
                    font=font,
                    stroke_width=stroke_width,
                    align=text_align,
                    spacing=interline,
                    width=img_width,
                    height=img_height,
                    allow_break=True,
                )

            # Add line breaks whenever needed
            text = "\n".join(
                self.__break_text(
                    width=img_width,
                    text=text,
                    font=font,
                    font_size=font_size,
                    stroke_width=stroke_width,
                    align=text_align,
                    spacing=interline,
                )
            )

            if img_height is None:
                img_height = self.__find_text_size(
                    text=text,
                    font=font,
                    font_size=font_size,
                    stroke_width=stroke_width,
                    align=text_align,
                    spacing=interline,
                    max_width=img_width,
                    allow_break=True,
                )[1]

        elif method == "label":
            if font_size is None and img_width is None:
                raise ValueError(
                    "Font size is mandatory when method is label and size is None"
                )

            if font_size is None:
                font_size = self.__find_optimum_font_size(
                    text=text,
                    font=font,
                    stroke_width=stroke_width,
                    align=text_align,
                    spacing=interline,
                    width=img_width,
                    height=img_height,
                )

            if img_width is None:
                img_width = self.__find_text_size(
                    text=text,
                    font=font,
                    font_size=font_size,
                    stroke_width=stroke_width,
                    align=text_align,
                    spacing=interline,
                )[0]

            if img_height is None:
                img_height = self.__find_text_size(
                    text=text,
                    font=font,
                    font_size=font_size,
                    stroke_width=stroke_width,
                    align=text_align,
                    spacing=interline,
                    max_width=img_width,
                )[1]

        img_width += left_margin + right_margin
        img_height += top_margin + bottom_margin

        # Trace the image
        img_mode = "RGBA" if transparent else "RGB"

        if bg_color is None and transparent:
            bg_color = (0, 0, 0, 0)

        img = Image.new(img_mode, (img_width, img_height), color=bg_color)
        if font:
            pil_font = ImageFont.truetype(font, font_size)
        else:
            pil_font = ImageFont.load_default(font_size)
        draw = ImageDraw.Draw(img)

        # Dont need allow break here, because we already breaked in caption
        text_width, text_height = self.__find_text_size(
            text=text,
            font=font,
            font_size=font_size,
            stroke_width=stroke_width,
            align=text_align,
            spacing=interline,
            max_width=img_width,
        )

        x = 0
        if horizontal_align == "right":
            x = img_width - text_width - left_margin - right_margin
        elif horizontal_align == "center":
            x = (img_width - left_margin - right_margin - text_width) / 2

        y = 0
        if vertical_align == "bottom":
            y = img_height - text_height - top_margin - bottom_margin
        elif vertical_align == "center":
            y = (img_height - top_margin - bottom_margin - text_height) / 2

        # We use baseline as our anchor because it is predictable and reliable
        # That mean we always have to use left baseline instead. Else we would
        # always have a useless margin (the diff between ascender and top) on any
        # text. That mean our Y is actually not from 0 for top, but need to be
        # increment by ascent, since we have to reference from baseline.
        (ascent, _) = pil_font.getmetrics()
        y += ascent

        # Add margins and stroke size to start point
        y += top_margin
        x += left_margin
        y += stroke_width
        x += stroke_width

        draw.multiline_text(
            xy=(x, y),
            text=text,
            fill=color,
            font=pil_font,
            spacing=interline,
            align=text_align,
            stroke_width=stroke_width,
            stroke_fill=stroke_color,
            anchor="ls",
        )

        # We just need the image as a numpy array
        img_numpy = np.array(img)

        ImageClip.__init__(
            self, img=img_numpy, transparent=transparent, duration=duration
        )
        self.text = text
        self.color = color
        self.stroke_color = stroke_color

    def __break_text(
        self, width, text, font, font_size, stroke_width, align, spacing
    ) -> List[str]:
        """Break text to never overflow a width"""
        img = Image.new("RGB", (1, 1))
        if font:
            font_pil = ImageFont.truetype(font, font_size)
        else:
            font_pil = ImageFont.load_default(font_size)
        draw = ImageDraw.Draw(img)

        lines = []
        current_line = ""

        # We try to break on spaces as much as possible
        # if a text dont contain spaces (ex chinese), we will break when possible
        last_space = 0
        for index, char in enumerate(text):
            if char == " ":
                last_space = index

            temp_line = current_line + char
            temp_left, temp_top, temp_right, temp_bottom = draw.multiline_textbbox(
                (0, 0),
                temp_line,
                font=font_pil,
                spacing=spacing,
                align=align,
                stroke_width=stroke_width,
            )
            temp_width = temp_right - temp_left

            if temp_width >= width:
                # If we had a space previously, add everything up to the space
                # and reset last_space and current_line else add everything up
                # to previous char
                if last_space:
                    lines.append(temp_line[0:last_space])
                    current_line = temp_line[last_space + 1 : index + 1]
                    last_space = 0
                else:
                    lines.append(current_line[0:index])
                    current_line = char
                    last_space = 0
            else:
                current_line = temp_line

        if current_line:
            lines.append(current_line)

        return lines

    def __find_text_size(
        self,
        text,
        font,
        font_size,
        stroke_width,
        align,
        spacing,
        max_width=None,
        allow_break=False,
    ) -> tuple[int, int]:
        """Find *real* dimensions a text will occupy, return a tuple (width, height)

        .. note::
            Text height calculation is quite complex due to how `Pillow` works.
            When calculating line height, `Pillow` actually uses the letter ``A``
            as a reference height, adding the spacing and the stroke width.
            However, ``A`` is a simple letter and does not account for ascent and
            descent, such as in ``Ô``.

            This means each line will be considered as having a "standard"
            height instead of the real maximum font size (``ascent + descent``).

            When drawing each line, `Pillow` will offset the new line by
            ``standard height * number of previous lines``.
            This mostly works, but if the spacing is not big enough,
            lines will overlap if a letter with an ascent (e.g., ``d``) is above
            a letter with a descent (e.g., ``p``).

            For our case, we use the baseline as the text anchor. This means that,
            no matter what, we need to draw the absolute top of our first line at
            ``0 + ascent + stroke_width`` to ensure the first pixel of any possible
            letter is aligned with the top border of the image (ignoring any
            additional margins, if needed).

            Therefore, our first line height will not start at ``0`` but at
            ``ascent + stroke_width``, and we need to account for that. Each
            subsequent line will then be drawn at
            ``index * standard height`` from this point. The position of the last
            line can be calculated as:
            ``(total_lines - 1) * standard height``.

            Finally, as we use the baseline as the text anchor, we also need to
            consider that the real size of the last line is not "standard" but
            rather ``standard + descent + stroke_width``.

            To summarize, the real height of the text is:
              ``initial padding + (lines - 1) * height + end padding``
            or:
              ``(ascent + stroke_width) + (lines - 1) * height + (descent + stroke_width)``
            or:
              ``real_font_size + (stroke_width * 2) + (lines - 1) * height``
        """
        img = Image.new("RGB", (1, 1))
        if font:
            font_pil = ImageFont.truetype(font, font_size)
        else:
            font_pil = ImageFont.load_default(font_size)
        ascent, descent = font_pil.getmetrics()
        real_font_size = ascent + descent
        draw = ImageDraw.Draw(img)

        # Compute individual line height with spaces using pillow internal method

        if max_width is not None and allow_break:
            lines = self.__break_text(
                width=max_width,
                text=text,
                font=font,
                font_size=font_size,
                stroke_width=stroke_width,
                align=align,
                spacing=spacing,
            )

            text = "\n".join(lines)

        # Use multiline textbbox to get width
        left, top, right, bottom = draw.multiline_textbbox(
            (0, 0),
            text,
            font=font_pil,
            spacing=spacing,
            align=align,
            stroke_width=stroke_width,
            anchor="ls",
        )

        # For height calculate manually as textbbox is not realiable
        try:
            # this disappeared in more recent versions of Pillow
            line_height = draw._multiline_spacing(font_pil, spacing, stroke_width)
            line_breaks = text.count("\n")
            lines_height = line_breaks * line_height
            paddings = real_font_size + stroke_width * 2
            height = int(lines_height + paddings)
        except AttributeError:
            height = int(bottom - top)

        return (int(right - left), height)

    def __find_optimum_font_size(
        self,
        text,
        font,
        stroke_width,
        align,
        spacing,
        width,
        height=None,
        allow_break=False,
    ):
        """Find the best font size to fit as optimally as possible
        in a box of some width and optionally height
        """
        max_font_size = width
        min_font_size = 1

        # Try find best size using bisection
        while min_font_size < max_font_size:
            avg_font_size = int((max_font_size + min_font_size) // 2)
            text_width, text_height = self.__find_text_size(
                text,
                font,
                avg_font_size,
                stroke_width,
                align,
                spacing,
                max_width=width,
                allow_break=allow_break,
            )

            if text_width <= width and (height is None or text_height <= height):
                min_font_size = avg_font_size + 1
            else:
                max_font_size = avg_font_size - 1

        # Check if the last font size tested fits within the given width and height
        text_width, text_height = self.__find_text_size(
            text,
            font,
            min_font_size,
            stroke_width,
            align,
            spacing,
            max_width=width,
            allow_break=allow_break,
        )
        if text_width <= width and (height is None or text_height <= height):
            return min_font_size
        else:
            return min_font_size - 1


class BitmapClip(VideoClip):
    """Clip made of color bitmaps. Mainly designed for testing purposes."""

    DEFAULT_COLOR_DICT = {
        "R": (255, 0, 0),
        "G": (0, 255, 0),
        "B": (0, 0, 255),
        "O": (0, 0, 0),
        "W": (255, 255, 255),
        "A": (89, 225, 62),
        "C": (113, 157, 108),
        "D": (215, 182, 143),
        "E": (57, 26, 252),
        "F": (225, 135, 33),
    }

    @convert_parameter_to_seconds(["duration"])
    def __init__(
        self, bitmap_frames, *, fps=None, duration=None, color_dict=None, is_mask=False
    ):
        """Creates a VideoClip object from a bitmap representation. Primarily used
        in the test suite.

        Parameters
        ----------

        bitmap_frames
          A list of frames. Each frame is a list of strings. Each string
          represents a row of colors. Each color represents an (r, g, b) tuple.
          Example input (2 frames, 5x3 pixel size)::

              [["RRRRR",
                "RRBRR",
                "RRBRR"],
               ["RGGGR",
                "RGGGR",
                "RGGGR"]]

        fps
          The number of frames per second to display the clip at. `duration` will
          calculated from the total number of frames. If both `fps` and `duration`
          are set, `duration` will be ignored.

        duration
          The total duration of the clip. `fps` will be calculated from the total
          number of frames. If both `fps` and `duration` are set, `duration` will
          be ignored.

        color_dict
          A dictionary that can be used to set specific (r, g, b) values that
          correspond to the letters used in ``bitmap_frames``.
          eg ``{"A": (50, 150, 150)}``.

          Defaults to::

              {
                "R": (255, 0, 0),
                "G": (0, 255, 0),
                "B": (0, 0, 255),
                "O": (0, 0, 0),  # "O" represents black
                "W": (255, 255, 255),
                # "A", "C", "D", "E", "F" represent arbitrary colors
                "A": (89, 225, 62),
                "C": (113, 157, 108),
                "D": (215, 182, 143),
                "E": (57, 26, 252),
              }

        is_mask
          Set to ``True`` if the clip is going to be used as a mask.
        """
        assert fps is not None or duration is not None

        self.color_dict = color_dict if color_dict else self.DEFAULT_COLOR_DICT

        frame_list = []
        for input_frame in bitmap_frames:
            output_frame = []
            for row in input_frame:
                output_frame.append([self.color_dict[color] for color in row])
            frame_list.append(np.array(output_frame))

        frame_array = np.array(frame_list)
        self.total_frames = len(frame_array)

        if fps is None:
            fps = self.total_frames / duration
        else:
            duration = self.total_frames / fps

        VideoClip.__init__(
            self,
            frame_function=lambda t: frame_array[int(t * fps)],
            is_mask=is_mask,
            duration=duration,
        )
        self.fps = fps

    def to_bitmap(self, color_dict=None):
        """Returns a valid bitmap list that represents each frame of the clip.
        If `color_dict` is not specified, then it will use the same `color_dict`
        that was used to create the clip.
        """
        color_dict = color_dict or self.color_dict

        bitmap = []
        for frame in self.iter_frames():
            bitmap.append([])
            for line in frame:
                bitmap[-1].append("")
                for pixel in line:
                    letter = list(color_dict.keys())[
                        list(color_dict.values()).index(tuple(pixel))
                    ]
                    bitmap[-1][-1] += letter

        return bitmap
