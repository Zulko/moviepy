"""
This module implements VideoClip (base class for video clips) and its
main subclasses:
- Animated clips:     VideofileClip, DirectoryClip
- Static image clips: ImageClip, ColorClip, TextClip,
"""

import os
import subprocess as sp
import multiprocessing
import tempfile
from copy import copy

from tqdm import tqdm
import numpy as np

from imageio import imread

import moviepy.audio.io as aio
from .io.ffmpeg_writer import ffmpeg_write_image, ffmpeg_write_video
from .io.ffmpeg_tools import ffmpeg_merge_video_audio
from .io.gif_writers import (write_gif,
                             write_gif_with_tempfiles,
                             write_gif_with_image_io)
from .tools.drawing import blit
from ..Clip import Clip
from ..config import get_setting

from ..tools import (subprocess_call,
                     verbose_print,
                     is_string,
                     deprecated_version_of,
                     extensions_dict, find_extension)

from ..decorators import (apply_to_mask,
                          requires_duration,
                          outplace,
                          add_mask_if_none,
                          convert_to_seconds,
                          convert_masks_to_RGB,
                          use_clip_fps_by_default)

import os
try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    DEVNULL = open(os.devnull, 'wb')


class VideoClip(Clip):
    """Base class for video clips.

    See ``VideofileClip``, ``ImageClip`` etc. for more user-friendly
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

    """

    def __init__(self, make_frame=None, ismask=False, duration=None,
                 has_constant_size=True):
        Clip.__init__(self)
        self.mask = None
        self.audio = None
        self.pos = lambda t: (0, 0)
        self.relative_pos = False
        if make_frame is not None:
            self.make_frame = make_frame
            self.size = self.get_frame(0).shape[:2][::-1]
        self.ismask = ismask
        self.has_constant_size=has_constant_size
        if duration is not None:
            self.duration = duration
            self.end = duration

    @property
    def w(self):
        return self.size[0]


    @property
    def h(self):
        return self.size[1]


    # ===============================================================
    # EXPORT OPERATIONS


    @convert_to_seconds(['t'])
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
        if im.dtype != "uint8":
            im = im.astype("uint8")

        if withmask and self.mask is not None:
            mask = 255 * self.mask.get_frame(t)
            im = np.dstack([im, mask]).astype('uint8')

        ffmpeg_write_image(filename, im)


    @requires_duration
    @use_clip_fps_by_default
    @convert_masks_to_RGB
    def write_videofile(self, filename, fps=None, codec=None,
                        bitrate=None, audio=True, audio_fps=44100,
                        preset="medium",
                        audio_nbytes=4, audio_codec=None,
                        audio_bitrate=None, audio_bufsize=2000,
                        temp_audiofile=None,
                        rewrite_audio=True, remove_temp=True,
                        write_logfile=False, verbose=True,
                        threads=None, ffmpeg_params=None):

        """Write the clip to a videofile.

        Parameters
        -----------

        filename
          Name of the video file to write in.
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
          of perfect quality, of smaller size than with ``rawvideo``


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

        audiofps
          frame rate to use when generating the sound.

        temp_audiofile
          the name of the temporary audiofile to be generated and
          incorporated in the the movie, if any.

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
          Choices are: ultrafast, superfast, fast, medium, slow, superslow.
          Note that this does not impact the quality of the video, only the
          size of the video file. So choose ultrafast when you are in a
          hurry and file size does not matter.

        threads
          Number of threads to use for ffmpeg. Can speed up the writing of
          the video on multicore computers

        ffmpeg_params
          Any additional ffmpeg parameters you would like to pass, as a list
          of terms, like ['-option1', 'value1', '-option2', 'value2']

        write_logfile
          If true, will write log files for the audio and the video.
          These will be files ending with '.log' with the name of the
          output file in them.



        Examples
        ========

        >>> from moviepy.editor import VideoFileClip
        >>> clip = VideoFileClip("myvideo.mp4").subclip(100,120)
        >>> clip.write_videofile("my_new_video.mp4")

        """

        name, ext = os.path.splitext(os.path.basename(filename))
        ext = ext[1:].lower()

        if codec is None:

            try:
                codec = extensions_dict[ext]['codec'][0]
            except KeyError:
                raise ValueError("MoviePy couldn't find the codec associated "
                                 "with the filename. Provide the 'codec' parameter in "
                                 "write_videofile.")

        if audio_codec is None:
            if (ext in ['ogv', 'webm']):
                audio_codec = 'libvorbis'
            else:
                audio_codec = 'libmp3lame'
        elif audio_codec == 'raw16':
            audio_codec = 'pcm_s16le'
        elif audio_codec == 'raw32':
            audio_codec = 'pcm_s32le'

        audiofile = audio if is_string(audio) else None
        make_audio = ((audiofile is None) and (audio == True) and
                      (self.audio is not None))

        if make_audio:
            # The audio will be the clip's audio
            if temp_audiofile is not None:
                audiofile = temp_audiofile

            else:

                # make a name for the temporary audio file

                if audio_codec in extensions_dict:
                    audio_ext = audio_codec
                else:
                    try:
                        audio_ext = find_extension(audio_codec)
                    except ValueError:

                        raise ValueError(
                            "The audio_codec you chose is unknown by MoviePy. "
                            "You should report this. In the meantime, you can specify a "
                            "temp_audiofile with the right extension in write_videofile.")

                audiofile = (name + Clip._TEMP_FILES_PREFIX +
                             "wvf_snd.%s" % audio_ext)

        # enough cpu for multiprocessing ? USELESS RIGHT NOW, WILL COME AGAIN
        # enough_cpu = (multiprocessing.cpu_count() > 1)

        verbose_print(verbose, "[MoviePy] >>>> Building video %s\n" % filename)

        if make_audio:
            self.audio.write_audiofile(audiofile, audio_fps,
                                       audio_nbytes, audio_bufsize,
                                       audio_codec, bitrate=audio_bitrate,
                                       write_logfile=write_logfile,
                                       verbose=verbose)

        ffmpeg_write_video(self, filename, fps, codec,
                           bitrate=bitrate,
                           preset=preset,
                           write_logfile=write_logfile,
                           audiofile = audiofile,
                           verbose=verbose, threads=threads,
                           ffmpeg_params=ffmpeg_params)

        if remove_temp and make_audio:
            os.remove(audiofile)

        verbose_print(verbose, "[MoviePy] >>>> Video ready: %s \n\n"%filename)


    @requires_duration
    @use_clip_fps_by_default
    @convert_masks_to_RGB
    def write_images_sequence(self, nameformat, fps=None, verbose=True,
                              withmask=True):
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
          will save the clip's mask (if any) as an alpha canal (PNGs only)

        verbose
          Verbose output ?


        Returns
        --------

        names_list
          A list of all the files generated.

        Notes
        ------

        The resulting image sequence can be read using e.g. the class
        ``DirectoryClip``.

        """

        verbose_print(verbose, "[MoviePy] Writing frames %s." % (nameformat))

        tt = np.arange(0, self.duration, 1.0 / fps)

        filenames = []
        total = int(self.duration / fps) + 1
        for i, t in tqdm(enumerate(tt), total=total):
            name = nameformat % (i + 1)
            filenames.append(name)
            self.save_frame(name, t, withmask=withmask)

        verbose_print(verbose,
                      "[MoviePy]: Done writing frames %s.\n\n" % (nameformat))

        return filenames



    @requires_duration
    @convert_masks_to_RGB
    def write_gif(self, filename, fps=None, program='imageio',
                  opt='wu', fuzz=1, verbose=True,
                  loop=0, dispose=False, colors=None, tempfiles=False):
        """ Write the VideoClip to a GIF file.

        Converts a VideoClip into an animated GIF using ImageMagick
        or ffmpeg.


        Parameters
        -----------

        filename
          Name of the resulting gif file.

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

        if program == 'imageio':
            write_gif_with_image_io(self, filename, fps=fps, opt=opt, loop=loop,
                                    verbose=verbose, colors=colors)
        
        elif tempfiles:
            write_gif_with_tempfiles(self, filename, fps=fps,
                                     program=program, opt=opt, fuzz=fuzz,
                                     verbose=verbose,
                                     loop=loop, dispose=dispose, colors=colors)
        else:
            write_gif(self, filename, fps=fps, program=program,
                      opt=opt, fuzz=fuzz, verbose=verbose, loop=loop,
                      dispose=dispose, colors=colors)

    # -----------------------------------------------------------------
    # F I L T E R I N G



    def subfx(self, fx, ta=0, tb=None, **kwargs):
        """ Apply a transformation to a part of the clip.

        Returns a new clip in which the function ``fun`` (clip->clip)
        has been applied to the subclip between times `ta` and `tb`
        (in seconds).

        Examples
        ---------

        >>> # The scene between times t=3s and t=6s in ``clip`` will be
        >>> # be played twice slower in ``newclip``
        >>> newclip = clip.subapply(lambda c:c.speedx(0.5) , 3,6)

        """

        left = None if (ta == 0) else self.subclip(0, ta)
        center = self.subclip(ta, tb).fx(fx, **kwargs)
        right = None if (tb is None) else self.subclip(t_start=tb)

        clips = [c for c in [left, center, right] if c is not None]

        # beurk, have to find other solution
        from moviepy.video.compositing.concatenate import concatenate_videoclips

        return concatenate_videoclips(clips).set_start(self.start)

    # IMAGE FILTERS


    def fl_image(self, image_func, apply_to=[]):
        """
        Modifies the images of a clip by replacing the frame
        `get_frame(t)` by another frame,  `image_func(get_frame(t))`
        """
        return self.fl(lambda gf, t: image_func(gf(t)), apply_to)

    # --------------------------------------------------------------
    # C O M P O S I T I N G


    def blit_on(self, picture, t):
        """
        Returns the result of the blit of the clip's frame at time `t`
        on the given `picture`, the position of the clip being given
        by the clip's ``pos`` attribute. Meant for compositing.
        """

        hf, wf = framesize = picture.shape[:2]

        if self.ismask and picture.max() != 0:
            return np.minimum(1, picture + self.blit_on(np.zeros(framesize), t))

        ct = t - self.start  # clip time

        # GET IMAGE AND MASK IF ANY

        img = self.get_frame(ct)
        mask = (None if (self.mask is None) else
                self.mask.get_frame(ct))
        hi, wi = img.shape[:2]

        # SET POSITION

        pos = self.pos(ct)

        # preprocess short writings of the position
        if isinstance(pos, str):
            pos = {'center': ['center', 'center'],
                   'left': ['left', 'center'],
                   'right': ['right', 'center'],
                   'top': ['center', 'top'],
                   'bottom': ['center', 'bottom']}[pos]
        else:
            pos = list(pos)

        # is the position relative (given in % of the clip's size) ?
        if self.relative_pos:
            for i, dim in enumerate(wf, hf):
                if not isinstance(pos[i], str):
                    pos[i] = dim * pos[i]

        if isinstance(pos[0], str):
            D = {'left': 0, 'center': (wf - wi) / 2, 'right': wf - wi}
            pos[0] = D[pos[0]]

        if isinstance(pos[1], str):
            D = {'top': 0, 'center': (hf - hi) / 2, 'bottom': hf - hi}
            pos[1] = D[pos[1]]

        pos = map(int, pos)

        return blit(img, picture, pos, mask=mask, ismask=self.ismask)


    def add_mask(self):
        """ Add a mask VideoClip to the VideoClip.

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
            make_frame = lambda t: np.ones(self.get_frame(t).shape[:2], dtype=float)
            mask = VideoClip(ismask=True, make_frame=make_frame)
            return self.set_mask(mask.set_duration(self.duration))


    def on_color(self, size=None, color=(0, 0, 0), pos=None,
                 col_opacity=None):
        """ Place the clip on a colored background.

        Returns a clip made of the current clip overlaid on a color
        clip of a possibly bigger size. Can serve to flatten transparent
        clips.

        Parameters
        -----------

        size
          Size (width, height) in pixels of the final clip.
          By default it will be the size of the current clip.

        bg_color
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
            pos = 'center'
        colorclip = ColorClip(size, color)

        if col_opacity is not None:
            colorclip = (ColorClip(size, color, duration=self.duration)
                         .set_opacity(col_opacity))
            result = CompositeVideoClip([colorclip, self.set_pos(pos)])
        else:
            result = CompositeVideoClip([self.set_pos(pos)],
                                        size=size,
                                        bg_color=color)

        if (isinstance(self, ImageClip) and (not hasattr(pos, "__call__"))
            and ((self.mask is None) or isinstance(self.mask, ImageClip))):
            new_result = result.to_ImageClip()
            if result.mask is not None:
                new_result.mask = result.mask.to_ImageClip()
            return new_result.set_duration(result.duration)

        return result


    @outplace
    def set_make_frame(self, mf):
        """ Change the clip's ``get_frame``.

        Returns a copy of the VideoClip instance, with the make_frame
        attribute set to `mf`.
        """
        self.make_frame = mf
        self.size = self.get_frame(0).shape[:2][::-1]


    @outplace
    def set_audio(self, audioclip):
        """ Attach an AudioClip to the VideoClip.

        Returns a copy of the VideoClip instance, with the `audio`
        attribute set to ``audio``, hich must be an AudioClip instance.
        """
        self.audio = audioclip


    @outplace
    def set_mask(self, mask):
        """ Set the clip's mask.

        Returns a copy of the VideoClip with the mask attribute set to
        ``mask``, which must be a greyscale (values in 0-1) VideoClip"""
        assert ( (mask is None) or mask.ismask )
        self.mask = mask


    @add_mask_if_none
    @outplace
    def set_opacity(self, op):
        """ Set the opacity/transparency level of the clip.

        Returns a semi-transparent copy of the clip where the mask is
        multiplied by ``op`` (any float, normally between 0 and 1).
        """

        self.mask = self.mask.fl_image(lambda pic: op * pic)


    @apply_to_mask
    @outplace
    def set_position(self, pos, relative=False):
        """ Set the clip's position in compositions.

        Sets the position that the clip will have when included
        in compositions. The argument ``pos`` can be either a couple
        ``(x,y)`` or a function ``t-> (x,y)``. `x` and `y` mark the
        location of the top left corner of the clip, and can be
        of several types.

        Examples
        ----------

        >>> clip.set_pos((45,150)) # x=45, y=150
        >>>
        >>> # clip horizontally centered, at the top of the picture
        >>> clip.set_pos(("center","top"))
        >>>
        >>> # clip is at 40% of the width, 70% of the height:
        >>> clip.set_pos((0.4,0.7), relative=True)
        >>>
        >>> # clip's position is horizontally centered, and moving up !
        >>> clip.set_pos(lambda t: ('center', 50+t) )

        """

        self.relative_pos = relative
        if hasattr(pos, '__call__'):
            self.pos = pos
        else:
            self.pos = lambda t: pos


    #--------------------------------------------------------------
    # CONVERSIONS TO OTHER TYPES



    @convert_to_seconds(['t'])
    def to_ImageClip(self, t=0, with_mask=True):
        """
        Returns an ImageClip made out of the clip's frame at time ``t``,
        which can be expressed in seconds (15.35), in (min, sec),
        in (hour, min, sec), or as a string: '01:03:05.35'.
        """
        newclip = ImageClip(self.get_frame(t), ismask=self.ismask)
        if with_mask and self.mask is not None:
            newclip.mask = self.mask.to_ImageClip(t)
        return newclip


    def to_mask(self, canal=0):
        """
        Returns a mask a video clip made from the clip.
        """
        if self.ismask:
            return self
        else:
            newclip = self.fl_image(lambda pic:
                                    1.0 * pic[:, :, canal] / 255)
            newclip.ismask = True
            return newclip


    def to_RGB(self):
        """
        Returns a non-mask video clip made from the mask video clip.
        """
        if self.ismask:
            f = lambda pic: np.dstack(3 * [255 * pic]).astype('uint8')
            newclip = self.fl_image(f)
            newclip.ismask = False
            return newclip
        else:
            return self

    #----------------------------------------------------------------
    # Audio


    @outplace
    def without_audio(self):
        """ Remove the clip's audio.

        Return a copy of the clip with audio set to None.

        """
        self.audio = None


    @outplace
    def afx(self, fun, *a, **k):
        """ Transform the clip's audio.

        Return a new clip whose audio has been transformed by ``fun``.

        """
        self.audio = self.audio.fx(fun, *a, **k)






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
        VideoClip.__init__(self, make_frame= make_frame,
                               ismask=ismask, duration=duration)






"""---------------------------------------------------------------------

    ImageClip (base class for all 'static clips') and its subclasses
    ColorClip and TextClip.
    I would have liked to put these in a separate file but Python is bad
    at cyclic imports.

---------------------------------------------------------------------"""


class ImageClip(VideoClip):
    """ Class for non-moving VideoClips.

    A video clip originating from a picture. This clip will simply
    display the given picture at all times.

    Examples
    ---------

    >>> clip = ImageClip("myHouse.jpeg")
    >>> clip = ImageClip( someArray ) # a Numpy array represent

    Parameters
    -----------

    img
      Any picture file (png, tiff, jpeg, etc.) or any array representing
      an RGB image (for instance a frame from a VideoClip).

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


    def __init__(self, img, ismask=False, transparent=True,
                 fromalpha=False, duration=None):

        VideoClip.__init__(self, ismask=ismask, duration=duration)

        if isinstance(img, str):
            img = imread(img)

        if len(img.shape) == 3:  # img is (now) a RGB(a) numpy array

            if img.shape[2] == 4:
                if fromalpha:
                    img = 1.0 * img[:, :, 3] / 255
                elif ismask:
                    img = 1.0 * img[:, :, 0] / 255
                elif transparent:
                    self.mask = ImageClip(
                        1.0 * img[:, :, 3] / 255, ismask=True)
                    img = img[:, :, :3]
            elif ismask:
                img = 1.0 * img[:, :, 0] / 255

        # if the image was just a 2D mask, it should arrive here
        # unchanged
        self.make_frame = lambda t: img
        self.size = img.shape[:2][::-1]
        self.img = img


    def fl(self, fl, apply_to=[], keep_duration=True):
        """ General transformation filter.

        Equivalent to VideoClip.fl . The result is no more an
        ImageClip, it has the class VideoClip (since it may be animated)
        """

        # When we use fl on an image clip it may become animated.
        # Therefore the result is not an ImageClip, just a VideoClip.
        newclip = VideoClip.fl(self, fl, apply_to=apply_to,
                               keep_duration=keep_duration)
        newclip.__class__ = VideoClip
        return newclip


    @outplace
    def fl_image(self, image_func, apply_to=[]):
        """ Image-transformation filter.

        Does the same as VideoClip.fl_image, but for ImageClip the
        tranformed clip is computed once and for all at the beginning,
        and not for each 'frame'.
        """

        arr = image_func(self.get_frame(0))
        self.size = arr.shape[:2][::-1]
        self.make_frame = lambda t: arr
        self.img = arr

        for attr in apply_to:
            if hasattr(self, attr):
                a = getattr(self, attr)
                if a is not None:
                    new_a = a.fl_image(image_func)
                    setattr(self, attr, new_a)


    @outplace
    def fl_time(self, time_func, apply_to=['mask', 'audio'],
                keep_duration=False):
        """ Time-transformation filter.

        Applies a transformation to the clip's timeline
        (see Clip.fl_time).

        This method does nothing for ImageClips (but it may affect their
        masks or their audios). The result is still an ImageClip.
        """

        for attr in apply_to:
            if hasattr(self, attr):
                a = getattr(self, attr)
                if a is not None:
                    new_a = a.fl_time(time_func)
                    setattr(self, attr, new_a)


# ##
#
# The old functions to_videofile, to_gif, to_images sequences have been
# replaced by the more explicite write_videofile, write_gif, etc.

VideoClip.set_pos = deprecated_version_of(VideoClip.set_position,
                                                'set_pos')
VideoClip.to_videofile = deprecated_version_of(VideoClip.write_videofile,
                                               'to_videofile')
VideoClip.to_gif = deprecated_version_of(VideoClip.write_gif, 'to_gif')
VideoClip.to_images_sequence = deprecated_version_of(VideoClip.write_images_sequence,
                                               'to_images_sequence')


class ColorClip(ImageClip):
    """ An ImageClip showing just one color.

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


    def __init__(self, size, col=(0, 0, 0), ismask=False, duration=None):
        w, h = size
        shape = (h, w) if np.isscalar(col) else (h, w, len(col))
        ImageClip.__init__(self, np.tile(col, w * h).reshape(shape),
                           ismask=ismask, duration=duration)


class TextClip(ImageClip):
    """ Class for autogenerated text clips.

    Creates an ImageClip originating from a script-generated text image.
    Requires ImageMagick.

    Parameters
    -----------

    txt
      A string of the text to write. Can be replaced by argument
      ``filename``.

    filename
      The name of a file in which there is the text to write.
      Can be provided instead of argument ``txt``

    size
      Size of the picture in pixels. Can be auto-set if
      method='label', but mandatory if method='caption'.
      the height can be None, it will then be auto-determined.

    bg_color
      Color of the background. See ``TextClip.list('color')``
      for a list of acceptable names.

    color
      Color of the background. See ``TextClip.list('color')`` for a
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
      nstance ``kerning=-1`` will make the letters 1 pixel nearer from
      ach other compared to the default spacing.

    align
      center | East | West | South | North . Will only work if ``method``
      is set to ``caption``

    transparent
      ``True`` (default) if you want to take into account the
      transparency in the image.

    """


    def __init__(self, txt=None, filename=None, size=None, color='black',
                 bg_color='transparent', fontsize=None, font='Courier',
                 stroke_color=None, stroke_width=1, method='label',
                 kerning=None, align='center', interline=None,
                 tempfilename=None, temptxt=None,
                 transparent=True, remove_temp=True,
                 print_cmd=False):


        if txt is not None:
            if temptxt is None:
                temptxt_fd, temptxt = tempfile.mkstemp(suffix='.txt')
                try:  # only in Python3 will this work
                    os.write(temptxt_fd, bytes(txt, 'UTF8'))
                except TypeError:  # oops, fall back to Python2
                    os.write(temptxt_fd, txt)
                os.close(temptxt_fd)
            txt = '@' + temptxt
        else:
            # use a file instead of a text.
            txt = "@%" + filename

        if size is not None:
            size = ('' if size[0] is None else str(size[0]),
                    '' if size[1] is None else str(size[1]))

        cmd = ( [get_setting("IMAGEMAGICK_BINARY"),
               "-background", bg_color,
               "-fill", color,
               "-font", font])

        if fontsize is not None:
            cmd += ["-pointsize", "%d" % fontsize]
        if kerning is not None:
            cmd += ["-kerning", "%0.1f" % kerning]
        if stroke_color is not None:
            cmd += ["-stroke", stroke_color, "-strokewidth",
                    "%.01f" % stroke_width]
        if size is not None:
            cmd += ["-size", "%sx%s" % (size[0], size[1])]
        if align is not None:
            cmd += ["-gravity", align]
        if interline is not None:
            cmd += ["-interline-spacing", "%d" % interline]

        if tempfilename is None:
            tempfile_fd, tempfilename = tempfile.mkstemp(suffix='.png')
            os.close(tempfile_fd)

        cmd += ["%s:%s" % (method, txt),
                "-type", "truecolormatte", "PNG32:%s" % tempfilename]

        if print_cmd:
            print( " ".join(cmd) )
        
        try:
            subprocess_call(cmd, verbose=False )
        except (IOError,OSError) as err:
            error = ("MoviePy Error: creation of %s failed because "
              "of the following error:\n\n%s.\n\n."%(filename, str(err))
               + ("This error can be due to the fact that "
                    "ImageMagick is not installed on your computer, or "
                    "(for Windows users) that you didn't specify the "
                    "path to the ImageMagick binary in file conf.py, or."
                    "that the path you specified is incorrect" ))
            raise IOError(error)

        ImageClip.__init__(self, tempfilename, transparent=transparent)
        self.txt = txt
        self.color = color
        self.stroke_color = stroke_color

        if remove_temp:
            if os.path.exists(tempfilename):
                os.remove(tempfilename)
            if os.path.exists(temptxt):
                os.remove(temptxt)


    @staticmethod
    def list(arg):
        """ Returns the list of all valid entries for the argument of
        ``TextClip`` given (can be ``font``, ``color``, etc...) """

        popen_params = {"stdout": sp.PIPE,
                        "stderr": DEVNULL,
                        "stdin": DEVNULL}

        if os.name == "nt":
            popen_params["creationflags"] = 0x08000000

        process = sp.Popen([get_setting("IMAGEMAGICK_BINARY"),
                            '-list', arg], **popen_params)
        result = process.communicate()[0]
        lines = result.splitlines()

        if arg == 'font':
            return [l[8:] for l in lines if l.startswith("  Font:")]
        elif arg == 'color':
            return [l.split(" ")[1] for l in lines[2:]]

    @staticmethod
    def search(string, arg):
        """ Returns the of all valid entries which contain ``string`` for the
           argument ``arg`` of ``TextClip``, for instance

           >>> # Find all the available fonts which contain "Courier"
           >>> print ( TextClip.search('Courier', 'font') )
 
        """
        string = string.lower()
        names_list = TextClip.list(arg)
        return [name for name in names_list if string in name.lower()]