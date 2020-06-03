"""
This module implements VideoClip (base class for video clips) and its
main subclasses:
- Animated clips:     VideofileClip, ImageSequenceClip
- Static image clips: ImageClip, ColorClip, TextClip,
"""
import os
import subprocess as sp
import tempfile

import numpy as np
import proglog
from imageio import imread, imsave

from moviepy.Clip import Clip
from moviepy.config import IMAGEMAGICK_BINARY
from moviepy.decorators import (
    add_mask_if_none,
    apply_to_mask,
    convert_masks_to_RGB,
    convert_path_to_string,
    convert_to_seconds,
    outplace,
    requires_duration,
    use_clip_fps_by_default,
    convert_path_to_string,
)
from moviepy.tools import extensions_dict, find_extension, subprocess_call
from moviepy.video.io.ffmpeg_writer import ffmpeg_write_video
from moviepy.video.io.gif_writers import (
    write_gif,
    write_gif_with_image_io,
    write_gif_with_tempfiles,
)
from moviepy.video.tools.drawing import blit


class VideoClip(Clip):
    """Base class for video clips.

    See ``VideoFileClip``, ``ImageClip`` etc. for more user-friendly
    classes.


    Parameters
    -----------

    ismask
      `True` if the clip is going to be used as a mask.


    Attributes
    ----------

    size
      The size of the clip, (width,heigth), in pixels.

    w, h
      The width and height of the clip, in pixels.

    ismask
      Boolean set to `True` if the clip is a mask.

    make_frame
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
        self, make_frame=None, ismask=False, duration=None, has_constant_size=True
    ):
        Clip.__init__(self)
        self.mask = None
        self.audio = None
        self.pos = lambda t: (0, 0)
        self.relative_pos = False
        self.layer = 0
        if make_frame:
            self.make_frame = make_frame
            self.size = self.get_frame(0).shape[:2][::-1]
        self.ismask = ismask
        self.has_constant_size = has_constant_size
        if duration is not None:
            self.duration = duration
            self.end = duration

    @property
    def w(self):
        return self.size[0]

    @property
    def h(self):
        return self.size[1]

    @property
    def aspect_ratio(self):
        return self.w / float(self.h)

    # ===============================================================
    # EXPORT OPERATIONS

    @convert_to_seconds(["t"])
    @convert_masks_to_RGB
    def save_frame(self, filename, t=0, withmask=True):
        """ Save a clip's frame to an image file.

        Saves the frame of clip corresponding to time ``t`` in
        'filename'. ``t`` can be expressed in seconds (15.35), in
        (min, sec), in (hour, min, sec), or as a string: '01:03:05.35'.

        If ``withmask`` is ``True`` the mask is saved in
        the alpha layer of the picture (only works with PNGs).

        """

        im = self.get_frame(t)
        if withmask and self.mask is not None:
            mask = 255 * self.mask.get_frame(t)
            im = np.dstack([im, mask]).astype("uint8")
        else:
            im = im.astype("uint8")

        imsave(filename, im)

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
        rewrite_audio=True,
        remove_temp=True,
        write_logfile=False,
        threads=None,
        ffmpeg_params=None,
        logger="bar",
    ):
        """Write the clip to a videofile.

        Parameters
        -----------

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

          ``'libx264'`` (default codec for file extension ``.mp4``)
          makes well-compressed videos (quality tunable using 'bitrate').


          ``'mpeg4'`` (other codec for extension ``.mp4``) can be an alternative
          to ``'libx264'``, and produces higher quality videos by default.


          ``'rawvideo'`` (use file extension ``.avi``) will produce
          a video of perfect quality, of possibly very huge size.


          ``png`` (use file extension ``.avi``) will produce a video
          of perfect quality, of smaller size than with ``rawvideo``.


          ``'libvorbis'`` (use file extension ``.ogv``) is a nice video
          format, which is completely free/ open source. However not
          everyone has the codecs installed by default on their machine.


          ``'libvpx'`` (use file extension ``.webm``) is tiny a video
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
          the name of the temporary audiofile, as a string or path-like object, to be created and
          then used to write the complete video, if any.

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
          Either "bar" for progress bar or None or any Proglog logger.

        Examples
        ========

        >>> from moviepy.editor import VideoFileClip
        >>> clip = VideoFileClip("myvideo.mp4").subclip(100,120)
        >>> clip.write_videofile("my_new_video.mp4")
        >>> clip.close()

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
        logger(message="Moviepy - Building video %s." % filename)
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

        ffmpeg_write_video(
            self,
            filename,
            fps,
            codec,
            bitrate=bitrate,
            preset=preset,
            write_logfile=write_logfile,
            audiofile=audiofile,
            threads=threads,
            ffmpeg_params=ffmpeg_params,
            logger=logger,
        )

        if remove_temp and make_audio:
            if os.path.exists(audiofile):
                os.remove(audiofile)
        logger(message="Moviepy - video ready %s" % filename)

    @requires_duration
    @use_clip_fps_by_default
    @convert_masks_to_RGB
    def write_images_sequence(self, nameformat, fps=None, withmask=True, logger="bar"):
        """ Writes the videoclip to a sequence of image files.

        Parameters
        -----------

        nameformat
          A filename specifying the numerotation format and extension
          of the pictures. For instance "frame%03d.png" for filenames
          indexed with 3 digits and PNG format. Also possible:
          "some_folder/frame%04d.jpeg", etc.

        fps
          Number of frames per second to consider when writing the
          clip. If not specified, the clip's ``fps`` attribute will
          be used if it has one.

        withmask
          will save the clip's mask (if any) as an alpha canal (PNGs only).

        logger
          Either 'bar' (progress bar) or None or any Proglog logger.


        Returns
        --------

        names_list
          A list of all the files generated.

        Notes
        ------

        The resulting image sequence can be read using e.g. the class
        ``ImageSequenceClip``.

        """
        logger = proglog.default_bar_logger(logger)
        logger(message="Moviepy - Writing frames %s." % nameformat)

        tt = np.arange(0, self.duration, 1.0 / fps)

        filenames = []
        for i, t in logger.iter_bar(t=list(enumerate(tt))):
            name = nameformat % i
            filenames.append(name)
            self.save_frame(name, t, withmask=withmask)
        logger(message="Moviepy - Done writing frames %s." % nameformat)

        return filenames

    @requires_duration
    @convert_masks_to_RGB
    @convert_path_to_string("filename")
    def write_gif(
        self,
        filename,
        fps=None,
        program="imageio",
        opt="nq",
        fuzz=1,
        loop=0,
        dispose=False,
        colors=None,
        tempfiles=False,
        logger="bar",
    ):
        """ Write the VideoClip to a GIF file.

        Converts a VideoClip into an animated GIF using ImageMagick
        or ffmpeg.

        Parameters
        -----------

        filename
          Name of the resulting gif file, as a string or a path-like object.

        fps
          Number of frames per second (see note below). If it
          isn't provided, then the function will look for the clip's
          ``fps`` attribute (VideoFileClip, for instance, have one).

        program
          Software to use for the conversion, either 'imageio' (this will use
          the library FreeImage through ImageIO), or 'ImageMagick', or 'ffmpeg'.

        opt
          Optimalization to apply. If program='imageio', opt must be either 'wu'
          (Wu) or 'nq' (Neuquant). If program='ImageMagick',
          either 'optimizeplus' or 'OptimizeTransparency'.

        fuzz
          (ImageMagick only) Compresses the GIF by considering that
          the colors that are less than fuzz% different are in fact
          the same.

        tempfiles
          Writes every frame to a file instead of passing them in the RAM.
          Useful on computers with little RAM. Can only be used with
          ImageMagick' or 'ffmpeg'.

        progress_bar
          If True, displays a progress bar


        Notes
        -----

        The gif will be playing the clip in real time (you can
        only change the frame rate). If you want the gif to be played
        slower than the clip you will use ::

            >>> # slow down clip 50% and make it a gif
            >>> myClip.speedx(0.5).to_gif('myClip.gif')

        """
        # A little sketchy at the moment, maybe move all that in write_gif,
        #  refactor a little... we will see.

        if program == "imageio":
            write_gif_with_image_io(
                self,
                filename,
                fps=fps,
                opt=opt,
                loop=loop,
                colors=colors,
                logger=logger,
            )
        elif tempfiles:
            # convert imageio opt variable to something that can be used with
            # ImageMagick
            opt = "optimizeplus" if opt == "nq" else "OptimizeTransparency"
            write_gif_with_tempfiles(
                self,
                filename,
                fps=fps,
                program=program,
                opt=opt,
                fuzz=fuzz,
                loop=loop,
                dispose=dispose,
                colors=colors,
                logger=logger,
            )
        else:
            # convert imageio opt variable to something that can be used with
            # ImageMagick
            opt = "optimizeplus" if opt == "nq" else "OptimizeTransparency"
            write_gif(
                self,
                filename,
                fps=fps,
                program=program,
                opt=opt,
                fuzz=fuzz,
                loop=loop,
                dispose=dispose,
                colors=colors,
                logger=logger,
            )

    # -----------------------------------------------------------------
    # F I L T E R I N G

    def subfx(self, fx, ta=0, tb=None, **kwargs):
        """Apply a transformation to a part of the clip.

        Returns a new clip in which the function ``fun`` (clip->clip)
        has been applied to the subclip between times `ta` and `tb`
        (in seconds).

        Examples
        ---------

        >>> # The scene between times t=3s and t=6s in ``clip`` will be
        >>> # be played twice slower in ``newclip``
        >>> newclip = clip.subapply(lambda c:c.speedx(0.5) , 3,6)

        """
        left = self.subclip(0, ta) if ta else None
        center = self.subclip(ta, tb).fx(fx, **kwargs)
        right = self.subclip(t_start=tb) if tb else None

        clips = [c for c in (left, center, right) if c]

        # beurk, have to find other solution
        from moviepy.video.compositing.concatenate import concatenate_videoclips

        return concatenate_videoclips(clips).set_start(self.start)

    # IMAGE FILTERS

    def fl_image(self, image_func, apply_to=None):
        """
        Modifies the images of a clip by replacing the frame
        `get_frame(t)` by another frame,  `image_func(get_frame(t))`
        """
        apply_to = apply_to or []
        return self.fl(lambda gf, t: image_func(gf(t)), apply_to)

    # --------------------------------------------------------------
    # C O M P O S I T I N G

    def fill_array(self, pre_array, shape=(0, 0)):
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

    def blit_on(self, picture, t):
        """
        Returns the result of the blit of the clip's frame at time `t`
        on the given `picture`, the position of the clip being given
        by the clip's ``pos`` attribute. Meant for compositing.
        """
        hf, wf = framesize = picture.shape[:2]

        if self.ismask and picture.max():
            return np.minimum(1, picture + self.blit_on(np.zeros(framesize), t))

        ct = t - self.start  # clip time

        # GET IMAGE AND MASK IF ANY

        img = self.get_frame(ct)
        mask = self.mask.get_frame(ct) if self.mask else None

        if mask is not None and (
            (img.shape[0] != mask.shape[0]) or (img.shape[1] != mask.shape[1])
        ):
            img = self.fill_array(img, mask.shape)

        hi, wi = img.shape[:2]

        # SET POSITION
        pos = self.pos(ct)

        # preprocess short writings of the position
        if isinstance(pos, str):
            pos = {
                "center": ["center", "center"],
                "left": ["left", "center"],
                "right": ["right", "center"],
                "top": ["center", "top"],
                "bottom": ["center", "bottom"],
            }[pos]
        else:
            pos = list(pos)

        # is the position relative (given in % of the clip's size) ?
        if self.relative_pos:
            for i, dim in enumerate([wf, hf]):
                if not isinstance(pos[i], str):
                    pos[i] = dim * pos[i]

        if isinstance(pos[0], str):
            D = {"left": 0, "center": (wf - wi) / 2, "right": wf - wi}
            pos[0] = D[pos[0]]

        if isinstance(pos[1], str):
            D = {"top": 0, "center": (hf - hi) / 2, "bottom": hf - hi}
            pos[1] = D[pos[1]]

        pos = map(int, pos)

        return blit(img, picture, pos, mask=mask, ismask=self.ismask)

    def add_mask(self):
        """Add a mask VideoClip to the VideoClip.

        Returns a copy of the clip with a completely opaque mask
        (made of ones). This makes computations slower compared to
        having a None mask but can be useful in many cases. Choose

        Set ``constant_size`` to  `False` for clips with moving
        image size.
        """
        if self.has_constant_size:
            mask = ColorClip(self.size, 1.0, ismask=True)
            return self.set_mask(mask.set_duration(self.duration))
        else:

            def make_frame(t):
                return np.ones(self.get_frame(t).shape[:2], dtype=float)

            mask = VideoClip(ismask=True, make_frame=make_frame)
            return self.set_mask(mask.set_duration(self.duration))

    def on_color(self, size=None, color=(0, 0, 0), pos=None, col_opacity=None):
        """Place the clip on a colored background.

        Returns a clip made of the current clip overlaid on a color
        clip of a possibly bigger size. Can serve to flatten transparent
        clips.

        Parameters
        -----------

        size
          Size (width, height) in pixels of the final clip.
          By default it will be the size of the current clip.

        color
          Background color of the final clip ([R,G,B]).

        pos
          Position of the clip in the final clip. 'center' is the default

        col_opacity
          Parameter in 0..1 indicating the opacity of the colored
          background.

        """
        from .compositing.CompositeVideoClip import CompositeVideoClip

        if size is None:
            size = self.size
        if pos is None:
            pos = "center"
        colorclip = ColorClip(size, color=color)

        if col_opacity is not None:
            colorclip = ColorClip(
                size, color=color, duration=self.duration
            ).set_opacity(col_opacity)
            result = CompositeVideoClip([colorclip, self.set_position(pos)])
        else:
            result = CompositeVideoClip(
                [self.set_position(pos)], size=size, bg_color=color
            )

        if (
            isinstance(self, ImageClip)
            and (not hasattr(pos, "__call__"))
            and ((self.mask is None) or isinstance(self.mask, ImageClip))
        ):
            new_result = result.to_ImageClip()
            if result.mask is not None:
                new_result.mask = result.mask.to_ImageClip()
            return new_result.set_duration(result.duration)

        return result

    @outplace
    def set_make_frame(self, mf):
        """Change the clip's ``get_frame``.

        Returns a copy of the VideoClip instance, with the make_frame
        attribute set to `mf`.
        """
        self.make_frame = mf
        self.size = self.get_frame(0).shape[:2][::-1]

    @outplace
    def set_audio(self, audioclip):
        """Attach an AudioClip to the VideoClip.

        Returns a copy of the VideoClip instance, with the `audio`
        attribute set to ``audio``, which must be an AudioClip instance.
        """
        self.audio = audioclip

    @outplace
    def set_mask(self, mask):
        """Set the clip's mask.

        Returns a copy of the VideoClip with the mask attribute set to
        ``mask``, which must be a greyscale (values in 0-1) VideoClip"""
        assert mask is None or mask.ismask
        self.mask = mask

    @add_mask_if_none
    @outplace
    def set_opacity(self, op):
        """Set the opacity/transparency level of the clip.

        Returns a semi-transparent copy of the clip where the mask is
        multiplied by ``op`` (any float, normally between 0 and 1).
        """
        self.mask = self.mask.fl_image(lambda pic: op * pic)

    @apply_to_mask
    @outplace
    def set_position(self, pos, relative=False):
        """Set the clip's position in compositions.

        Sets the position that the clip will have when included
        in compositions. The argument ``pos`` can be either a couple
        ``(x,y)`` or a function ``t-> (x,y)``. `x` and `y` mark the
        location of the top left corner of the clip, and can be
        of several types.

        Examples
        ----------

        >>> clip.set_position((45,150)) # x=45, y=150
        >>>
        >>> # clip horizontally centered, at the top of the picture
        >>> clip.set_position(("center","top"))
        >>>
        >>> # clip is at 40% of the width, 70% of the height:
        >>> clip.set_position((0.4,0.7), relative=True)
        >>>
        >>> # clip's position is horizontally centered, and moving up !
        >>> clip.set_position(lambda t: ('center', 50+t) )

        """
        self.relative_pos = relative
        if hasattr(pos, "__call__"):
            self.pos = pos
        else:
            self.pos = lambda t: pos

    @apply_to_mask
    @outplace
    def set_layer(self, layer):
        """Set the clip's layer in compositions. Clips with a greater ``layer``
        attribute will be displayed on top of others.

        Note: Only has effect when the clip is used in a CompositeVideoClip."""
        self.layer = layer

    # --------------------------------------------------------------
    # CONVERSIONS TO OTHER TYPES

    @convert_to_seconds(["t"])
    def to_ImageClip(self, t=0, with_mask=True, duration=None):
        """
        Returns an ImageClip made out of the clip's frame at time ``t``,
        which can be expressed in seconds (15.35), in (min, sec),
        in (hour, min, sec), or as a string: '01:03:05.35'.
        """
        newclip = ImageClip(self.get_frame(t), ismask=self.ismask, duration=duration)
        if with_mask and self.mask is not None:
            newclip.mask = self.mask.to_ImageClip(t)
        return newclip

    def to_mask(self, canal=0):
        """Return a mask a video clip made from the clip."""
        if self.ismask:
            return self
        else:
            newclip = self.fl_image(lambda pic: 1.0 * pic[:, :, canal] / 255)
            newclip.ismask = True
            return newclip

    def to_RGB(self):
        """Return a non-mask video clip made from the mask video clip."""
        if self.ismask:
            newclip = self.fl_image(
                lambda pic: np.dstack(3 * [255 * pic]).astype("uint8")
            )
            newclip.ismask = False
            return newclip
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

    @outplace
    def afx(self, fun, *a, **k):
        """Transform the clip's audio.

        Return a new clip whose audio has been transformed by ``fun``.

        """
        self.audio = self.audio.fx(fun, *a, **k)


class DataVideoClip(VideoClip):
    """
    Class of video clips whose successive frames are functions
    of successive datasets

    Parameters
    -----------
    data
      A liste of datasets, each dataset being used for one frame of the clip

    data_to_frame
      A function d -> video frame, where d is one element of the list `data`

    fps
      Number of frames per second in the animation

    Examples
    ---------
    """

    def __init__(self, data, data_to_frame, fps, ismask=False, has_constant_size=True):
        self.data = data
        self.data_to_frame = data_to_frame
        self.fps = fps

        def make_frame(t):
            return self.data_to_frame(self.data[int(self.fps * t)])

        VideoClip.__init__(
            self,
            make_frame,
            ismask=ismask,
            duration=1.0 * len(data) / fps,
            has_constant_size=has_constant_size,
        )


class UpdatedVideoClip(VideoClip):
    """
    Class of clips whose make_frame requires some objects to
    be updated. Particularly practical in science where some
    algorithm needs to make some steps before a new frame can
    be generated.

    UpdatedVideoClips have the following make_frame:

    >>> def make_frame(t):
    >>>     while self.world.clip_t < t:
    >>>         world.update() # updates, and increases world.clip_t
    >>>     return world.to_frame()

    Parameters
    -----------

    world
      An object with the following attributes:
      - world.clip_t : the clip's time corresponding to the
          world's state
      - world.update() : update the world's state, (including
        increasing world.clip_t of one time step)
      - world.to_frame() : renders a frame depending on the world's state

    ismask
      True if the clip is a WxH mask with values in 0-1

    duration
      Duration of the clip, in seconds

    """

    def __init__(self, world, ismask=False, duration=None):
        self.world = world

        def make_frame(t):
            while self.world.clip_t < t:
                world.update()
            return world.to_frame()

        VideoClip.__init__(
            self, make_frame=make_frame, ismask=ismask, duration=duration
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
    ---------

    >>> clip = ImageClip("myHouse.jpeg")
    >>> clip = ImageClip( someArray ) # a Numpy array represent

    Parameters
    -----------

    img
      Any picture file (png, tiff, jpeg, etc.) as a string or a path-like object,
      or any array representing an RGB image (for instance a frame from a VideoClip).

    ismask
      Set this parameter to `True` if the clip is a mask.

    transparent
      Set this parameter to `True` (default) if you want the alpha layer
      of the picture (if it exists) to be used as a mask.

    Attributes
    -----------

    img
      Array representing the image of the clip.

    """

    def __init__(
        self, img, ismask=False, transparent=True, fromalpha=False, duration=None
    ):
        VideoClip.__init__(self, ismask=ismask, duration=duration)

        if not isinstance(img, np.ndarray):
            # img is a string or path-like object, so read it in from disk
            img = imread(img)

        if len(img.shape) == 3:  # img is (now) a RGB(a) numpy array

            if img.shape[2] == 4:
                if fromalpha:
                    img = 1.0 * img[:, :, 3] / 255
                elif ismask:
                    img = 1.0 * img[:, :, 0] / 255
                elif transparent:
                    self.mask = ImageClip(1.0 * img[:, :, 3] / 255, ismask=True)
                    img = img[:, :, :3]
            elif ismask:
                img = 1.0 * img[:, :, 0] / 255

        # if the image was just a 2D mask, it should arrive here
        # unchanged
        self.make_frame = lambda t: img
        self.size = img.shape[:2][::-1]
        self.img = img

    def fl(self, fl, apply_to=None, keep_duration=True):
        """General transformation filter.

        Equivalent to VideoClip.fl . The result is no more an
        ImageClip, it has the class VideoClip (since it may be animated)
        """
        if apply_to is None:
            apply_to = []
        # When we use fl on an image clip it may become animated.
        # Therefore the result is not an ImageClip, just a VideoClip.
        newclip = VideoClip.fl(self, fl, apply_to=apply_to, keep_duration=keep_duration)
        newclip.__class__ = VideoClip
        return newclip

    @outplace
    def fl_image(self, image_func, apply_to=None):
        """Image-transformation filter.

        Does the same as VideoClip.fl_image, but for ImageClip the
        tranformed clip is computed once and for all at the beginning,
        and not for each 'frame'.
        """
        if apply_to is None:
            apply_to = []
        arr = image_func(self.get_frame(0))
        self.size = arr.shape[:2][::-1]
        self.make_frame = lambda t: arr
        self.img = arr

        for attr in apply_to:
            a = getattr(self, attr, None)
            if a is not None:
                new_a = a.fl_image(image_func)
                setattr(self, attr, new_a)

    @outplace
    def fl_time(self, time_func, apply_to=None, keep_duration=False):
        """Time-transformation filter.

        Applies a transformation to the clip's timeline
        (see Clip.fl_time).

        This method does nothing for ImageClips (but it may affect their
        masks or their audios). The result is still an ImageClip.
        """
        if apply_to is None:
            apply_to = ["mask", "audio"]
        for attr in apply_to:
            a = getattr(self, attr, None)
            if a is not None:
                new_a = a.fl_time(time_func)
                setattr(self, attr, new_a)


class ColorClip(ImageClip):
    """An ImageClip showing just one color.

    Parameters
    -----------

    size
      Size (width, height) in pixels of the clip.

    color
      If argument ``ismask`` is False, ``color`` indicates
      the color in RGB of the clip (default is black). If `ismask``
      is True, ``color`` must be  a float between 0 and 1 (default is 1)

    ismask
      Set to true if the clip will be used as a mask.

    """

    def __init__(self, size, color=None, ismask=False, duration=None):
        w, h = size

        if ismask:
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
            shape = (h, w, len(color))

        super().__init__(
            np.tile(color, w * h).reshape(shape), ismask=ismask, duration=duration
        )


class TextClip(ImageClip):
    """Class for autogenerated text clips.

    Creates an ImageClip originating from a script-generated text image.
    Requires ImageMagick.

    Parameters
    -----------

    txt
      A string of the text to write. Can be replaced by argument
      ``filename``.

    filename
      The name of a file in which there is the text to write,
      as a string or a path-like object.
      Can be provided instead of argument ``txt``

    size
      Size of the picture in pixels. Can be auto-set if
      method='label', but mandatory if method='caption'.
      the height can be None, it will then be auto-determined.

    bg_color
      Color of the background. See ``TextClip.list('color')``
      for a list of acceptable names.

    color
      Color of the text. See ``TextClip.list('color')`` for a
      list of acceptable names.

    font
      Name of the font to use. See ``TextClip.list('font')`` for
      the list of fonts you can use on your computer.

    stroke_color
      Color of the stroke (=contour line) of the text. If ``None``,
      there will be no stroke.

    stroke_width
      Width of the stroke, in pixels. Can be a float, like 1.5.

    method
      Either 'label' (default, the picture will be autosized so as to fit
      exactly the size) or 'caption' (the text will be drawn in a picture
      with fixed size provided with the ``size`` argument). If `caption`,
      the text will be wrapped automagically (sometimes it is buggy, not
      my fault, complain to the ImageMagick crew) and can be aligned or
      centered (see parameter ``align``).

    kerning
      Changes the default spacing between letters. For
      instance ``kerning=-1`` will make the letters 1 pixel nearer from
      ach other compared to the default spacing.

    align
      center | East | West | South | North . Will only work if ``method``
      is set to ``caption``

    transparent
      ``True`` (default) if you want to take into account the
      transparency in the image.

    """

    @convert_path_to_string("filename")
    def __init__(
        self,
        txt=None,
        filename=None,
        size=None,
        color="black",
        bg_color="transparent",
        fontsize=None,
        font="Courier",
        stroke_color=None,
        stroke_width=1,
        method="label",
        kerning=None,
        align="center",
        interline=None,
        tempfilename=None,
        temptxt=None,
        transparent=True,
        remove_temp=True,
        print_cmd=False,
    ):

        if txt is not None:
            if temptxt is None:
                temptxt_fd, temptxt = tempfile.mkstemp(suffix=".txt")
                try:  # only in Python3 will this work
                    os.write(temptxt_fd, bytes(txt, "UTF8"))
                except TypeError:  # oops, fall back to Python2
                    os.write(temptxt_fd, txt)
                os.close(temptxt_fd)
            txt = "@" + temptxt
        else:
            # use a file instead of a text.
            txt = "@%" + filename

        if size is not None:
            size = (
                "" if size[0] is None else str(size[0]),
                "" if size[1] is None else str(size[1]),
            )

        cmd = [
            IMAGEMAGICK_BINARY,
            "-background",
            bg_color,
            "-fill",
            color,
            "-font",
            font,
        ]

        if fontsize is not None:
            cmd += ["-pointsize", "%d" % fontsize]
        if kerning is not None:
            cmd += ["-kerning", "%0.1f" % kerning]
        if stroke_color is not None:
            cmd += ["-stroke", stroke_color, "-strokewidth", "%.01f" % stroke_width]
        if size is not None:
            cmd += ["-size", "%sx%s" % (size[0], size[1])]
        if align is not None:
            cmd += ["-gravity", align]
        if interline is not None:
            cmd += ["-interline-spacing", "%d" % interline]

        if tempfilename is None:
            tempfile_fd, tempfilename = tempfile.mkstemp(suffix=".png")
            os.close(tempfile_fd)

        cmd += [
            "%s:%s" % (method, txt),
            "-type",
            "truecolormatte",
            "PNG32:%s" % tempfilename,
        ]

        if print_cmd:
            print(" ".join(cmd))

        try:
            subprocess_call(cmd, logger=None)
        except (IOError, OSError) as err:
            error = (
                f"MoviePy Error: creation of {filename} failed because of the "
                f"following error:\n\n{err}.\n\n."
                "This error can be due to the fact that ImageMagick "
                "is not installed on your computer, or (for Windows "
                "users) that you didn't specify the path to the "
                "ImageMagick binary. Check the documentation."
            )
            raise IOError(error)

        ImageClip.__init__(self, tempfilename, transparent=transparent)
        self.txt = txt
        self.color = color
        self.stroke_color = stroke_color

        if remove_temp:
            if tempfilename is not None and os.path.exists(tempfilename):
                os.remove(tempfilename)
            if temptxt is not None and os.path.exists(temptxt):
                os.remove(temptxt)

    @staticmethod
    def list(arg):
        """Returns a list of all valid entries for the ``font`` or ``color`` argument of
        ``TextClip``"""

        popen_params = {"stdout": sp.PIPE, "stderr": sp.DEVNULL, "stdin": sp.DEVNULL}

        if os.name == "nt":
            popen_params["creationflags"] = 0x08000000

        process = sp.Popen(
            [IMAGEMAGICK_BINARY, "-list", arg], encoding="utf-8", **popen_params
        )
        result = process.communicate()[0]
        lines = result.splitlines()

        if arg == "font":
            # Slice removes first 8 characters: "  Font: "
            return [l[8:] for l in lines if l.startswith("  Font:")]
        elif arg == "color":
            # Each line is of the format "aqua  srgb(0,255,255)  SVG" so split on space and take
            # the first item to get the color name.
            # The first 5 lines are header information, not colors, so ignore
            return [l.split(" ")[0] for l in lines[5:]]
        else:
            raise Exception("Moviepy Error: Argument must equal 'font' or 'color'")

    @staticmethod
    def search(string, arg):
        """Returns the of all valid entries which contain ``string`` for the
           argument ``arg`` of ``TextClip``, for instance

           >>> # Find all the available fonts which contain "Courier"
           >>> print(TextClip.search('Courier', 'font'))

        """
        string = string.lower()
        names_list = TextClip.list(arg)
        return [name for name in names_list if string in name.lower()]


class BitmapClip(VideoClip):
    def __init__(self, bitmap_frames, *, color_dict=None, ismask=False):
        """
        Creates a VideoClip object from a bitmap representation. Primarily used in the test suite.

        Parameters
        -----------

        bitmap_frames
          A list of frames. Each frame is a list of strings. Each string represents a row of colors.
          Each color represents an (r, g, b) tuple.
          Example input (2 frames, 5x3 pixel size):
          [["RRRRR",
            "RRBRR",
            "RRBRR"],
           ["RGGGR",
            "RGGGR",
            "RGGGR"]]

        color_dict
          A dictionary that can be used to set specific (r, g, b) values that correspond
          to the letters used in ``bitmap_frames``.
          eg ``{"A": (50, 150, 150)}``.

          Defaults to
          ::
          {
            "R": (255, 0, 0),
            "G": (0, 255, 0),
            "B": (0, 0, 255),
            "O": (0, 0, 0),  # "O" represents black
            "W": (255, 255, 255),
            "A": (89, 225, 62),  # "A", "C", "D", "E", "F" represent arbitrary colors
            "C": (113, 157, 108),
            "D": (215, 182, 143),
            "E": (57, 26, 252),
          }

        ismask
          Set to ``True`` if the clip is going to be used as a mask.

        """
        if color_dict:
            self.color_dict = color_dict
        else:
            self.color_dict = {
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

        frame_list = []
        for input_frame in bitmap_frames:
            output_frame = []
            for row in input_frame:
                output_frame.append([self.color_dict[color] for color in row])
            frame_list.append(np.array(output_frame))

        frame_array = np.array(frame_list)
        VideoClip.__init__(
            self, make_frame=lambda t: frame_array[int(t)], ismask=ismask
        )

        self.total_frames = len(frame_array)
        self.fps = None

    @convert_to_seconds(["duration"])
    def set_duration(self, duration, change_end=True):
        """
        Sets the ``duration`` attribute of the clip.
        Additionally, if the clip's ``fps`` attribute has not already been set, it will 
        be set based on the new duration and the total number of frames.
        """
        if self.fps is None:
            return (
                super()
                .set_duration(duration=duration, change_end=change_end)
                .set_fps(int(self.total_frames / duration))
            )

        return super().set_duration(duration=duration, change_end=change_end)

    def set_fps(self, fps):
        """
        Sets the ``fps`` attribute of the clip.
        Additionally, if the clip's ``duration`` attribute has not already been set, it will 
        be set based on the new fps and the total number of frames.
        """
        total_duration = self.total_frames / fps
        if self.duration is None or self.duration > total_duration:
            return super().set_fps(fps).set_duration(total_duration)
        return super().set_fps(fps)

    def to_bitmap(self, color_dict=None):
        """
        Returns a valid bitmap list that represents each frame of the clip.
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
