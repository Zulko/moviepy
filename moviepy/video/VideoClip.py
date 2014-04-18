"""
This module implements VideoClip (base class for video clips) and its
main subclasses:
- Animated clips:     VideofileClip, DirectoryClip
- Static image clips: ImageClip, ColorClip, TextClip,
"""

import os
import subprocess
import multiprocessing
import tempfile
from copy import copy
from tqdm import tqdm


import numpy as np

from moviepy.decorators import  (apply_to_mask,
                                 requires_duration,
                                 outplace,
                                 add_mask_if_none)
from moviepy.tools import subprocess_call, sys_write_flush

import moviepy.audio.io as aio
from .io.ffmpeg_writer import ffmpeg_write_image, ffmpeg_write_video
from .io.ffmpeg_reader import ffmpeg_read_image
from .io.ffmpeg_tools import ffmpeg_merge_video_audio

from .tools.drawing import blit
from ..Clip import Clip
from ..conf import FFMPEG_BINARY, IMAGEMAGICK_BINARY


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

    get_frame
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

    def __init__(self, ismask=False, get_frame=None):
        Clip.__init__(self)
        self.mask = None
        self.audio = None
        self.pos = lambda t: (0, 0)
        self.relative_pos = False
        if get_frame:
            self.get_frame = get_frame
            self.size =get_frame(0).shape[:2][::-1]
        self.ismask = ismask

    @property
    def w(self):
        return self.size[0]



    @property
    def h(self):
        return self.size[1]



    # ===============================================================
    # EXPORT OPERATIONS



    def save_frame(self, filename, t=0, savemask=False):
        """ Save a clip's frame to an image file.

        Saves the frame of clip corresponding to time ``t`` in
        'filename'. If ``savemask`` is ``True`` the mask is saved in
        the alpha layer of the picture.

        """
        im = self.get_frame(t)
        if savemask and self.mask is not None:
            mask = 255 * self.mask.get_frame(t)
            im = np.dstack([im, mask]).astype('uint8')
        ffmpeg_write_image(filename, im)



    def to_videofile(self, filename, fps=24, codec='libx264',
                 bitrate=None, audio=True, audio_fps=44100,
                 audio_nbytes = 4, audio_codec= 'libvorbis',
                 audio_bitrate = None, audio_bufsize = 2000,
                 temp_audiofile=None,
                 rewrite_audio = True, remove_temp = True,
                 write_logfile=False,
                 para = False, verbose = True):
        """Write the clip to a videofile.

        Parameters
        -----------

        filename
          Name of the video file. The extension must correspond to the
          codec used (see below), ar simply be '.avi'.

        fps
          Number of frames per second in the resulting video file.

        codec
          Codec to use for image encoding. Can be any codec supported
          by ffmpeg.

          ``'rawvideo'``, ``'png'`` will produce a raw video,
          of perfect quality, but possibly very huge size. 'png' is
          is lossless and produces smaller files than 'rawvideo'.

          ``'mpeg4'`` produces nice quality, very well compressed
          videos.

          ``'libx264'`` (default) is a little better than 'mpeg4',
          a little heavier.

        audio
          Either ``True``, ``False``, or a file name.
          If ``True`` and the clip has an audio clip attached, this
          audio clip will be incorporated as a soundtrack in the movie.
          If ``audio`` is the name of an audio file, this audio file
          will be incorporated as a soundtrack in the movie.

        audiofps
          frame rate to use when writing the sound.

        temp_wav
          the name of the temporary audiofile to be generated and
          incorporated in the the movie, if any.

        """

        name, ext = os.path.splitext(os.path.basename(filename))

        if audio_codec == 'raw16':
            audio_codec = 'pcm_s16le'
        elif audio_codec == 'raw32':
            audio_codec = 'pcm_s32le'

        def verbose_print(s):
            if verbose: sys_write_flush(s)

        if isinstance(audio, str):
            # audio is some audiofile it is maybe not a wav file. It is
            # NOT temporary file, it will NOT be removed at the end.
            temp_audiofile = audio
            make_audio = False
            merge_audio = True

        elif self.audio is None:
            # audio not provided as a file and no clip.audio
            make_audio = merge_audio =  False

        elif audio:
            # The audio will be the clip's audio
            if temp_audiofile is None:

                # make a name for the temporary audio file

                D_ext = {'libmp3lame': 'mp3',
                       'libvorbis':'ogg',
                       'libfdk_aac':'m4a',
                       'aac':'m4a',
                       'pcm_s16le':'wav',
                       'pcm_s32le': 'wav'}

                if audio_codec in D_ext.values():
                    audio_ext = audio_codec
                else:
                    if audio_codec in D_ext.keys():
                        audio_ext = D_ext[audio_codec]
                    else:
                        raise ValueError('audio_codec for file'
                                          '%d unkown !'%filename)

                temp_audiofile = (name+Clip._TEMP_FILES_PREFIX +
                            "to_videofile_SOUND%s"%audio_ext)

            make_audio = ( (not os.path.exists(temp_audiofile))
                            or rewrite_audio)
            merge_audio = True

        else:

            make_audio = False
            merge_audio = False

        if merge_audio:

            # make a name for the temporary video file
            videofile = (name + Clip._TEMP_FILES_PREFIX +
                         "to_videofile%s"%ext)

        else:

            videofile = filename

        # enough cpu for multiprocessing ?
        enough_cpu = (multiprocessing.cpu_count() > 2)

        verbose_print("\nMoviePy: building video file %s\n"%filename
                      +40*"-"+"\n")

        if para and make_audio and  enough_cpu:

            # Parallelize
            verbose_print("Writing audio/video in parrallel.\n")
            audioproc = multiprocessing.Process(
                    target=self.audio.to_audiofile,
                    args=(temp_audiofile,audio_fps,audio_nbytes,
                          audio_bufsize,audio_codec,
                          audio_bitrate,
                          verbose))

            audioproc.start()
            
            ffmpeg_write_video(self, 
                               videofile, fps, codec,
                               bitrate=bitrate,
                               write_logfile=write_logfile,
                               verbose=verbose)
            audioproc.join()
            if audioproc.exitcode:
                print ("WARNING: something went wrong with the audio"+
                       " writing, Exit code %d"%audioproc.exitcode)
        else:

            # Don't parallelize
            if make_audio:
                self.audio.to_audiofile(temp_audiofile,audio_fps,
                                        audio_nbytes, audio_bufsize,
                                        audio_codec, audio_bitrate,
                                        verbose)

            ffmpeg_write_video(self,
                               videofile, fps, codec,
                               bitrate=bitrate,
                               write_logfile=write_logfile,
                               verbose=verbose)

        # Merge with audio if any and trash temporary files.
        if merge_audio:

            verbose_print("\n\nNow merging video and audio:\n")
            ffmpeg_merge_video_audio(videofile,temp_audiofile,
                                  filename, ffmpeg_output=True)

            if remove_temp:
                os.remove(videofile)
                if not isinstance(audio,str):
                    os.remove(temp_audiofile)
            verbose_print("\nYour video is ready ! Fingers crossed"
                          " for the Oscars !\n")


    def to_images_sequence(self, nameformat, fps=None, verbose=True):
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

        if verbose:
          print( "MoviePy: Writing frames %s."%(nameformat))

        if fps is None:
            fps = self.fps

        tt = np.arange(0, self.duration, 1.0/fps)

        filenames = []
        total = int(self.duration/fps)+1
        for i, t in tqdm(enumerate(tt), total=total):
            name = nameformat%(i+1)
            filenames.append(name)
            self.save_frame(name, t, savemask=True)

        if verbose:
          print( "MoviePy: Done writing frames %s."%(nameformat))

        return filenames



    def to_gif(self, filename, fps=None, program= 'ImageMagick',
            opt="OptimizeTransparency", fuzz=1, verbose=True,
            loop=0, dispose=False):
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
          Software to use for the conversion, either 'ImageMagick' or
          'ffmpeg'.

        opt
          (ImageMagick only) optimalization to apply, either
          'optimizeplus' or 'OptimizeTransparency'.

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

        def verbose_print(s):
            if verbose: sys_write_flush(s)

        if fps is None:
            fps = self.fps

        fileName, fileExtension = os.path.splitext(filename)
        tt = np.arange(0,self.duration, 1.0/fps)
        tempfiles = []

        verbose_print("\nMoviePy: building GIF file %s\n"%filename
                      +40*"-"+"\n")

        verbose_print("Generating GIF frames.\n")

        total = int(self.duration/fps)+1
        for i, t in tqdm(enumerate(tt), total=total):

            name = "%s_GIFTEMP%04d.png"%(fileName, i+1)
            tempfiles.append(name)
            self.save_frame(name, t, savemask=True)

        verbose_print("Done generating GIF frames.\n")

        delay = int(100.0/fps)

        if program == "ImageMagick":

            cmd = [IMAGEMAGICK_BINARY,
                  '-delay' , '%d'%delay,
                  "-dispose" ,"%d"%(2 if dispose else 1),
                  "-loop" , "%d"%loop,
                  "%s_GIFTEMP*.png"%fileName,
                  "-coalesce",
                  "-fuzz", "%02d"%fuzz + "%",
                  "-layers", "%s"%opt,
                  "%s"%filename]

        elif program == "ffmpeg":

            cmd = [FFMPEG_BINARY, '-y',
                   '-f', 'image2',
                   '-i', fileName+'_GIFTEMP%04d.png',
                   '-r',str(fps),
                   filename]


        subprocess_call( cmd, verbose = verbose )

        for f in tempfiles:
            os.remove(f)



    #-----------------------------------------------------------------
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
        left = None if (ta == 0) else self.subclip(0, tb=ta)
        center = self.subclip(ta, tb).fx(**kwargs)
        right = None if (tb is None) else self.subclip(ta=tb)

        clips = [c for c in [left, center, right] if c != None]
        cc = VideoClip.concat(clips)

        if self.start != None:
            cc = cc.set_start(self.start)

        return cc


    # IMAGE FILTERS


    def fl_image(self, image_func, apply_to=[]):
        """
        Modifies the images of a clip by replacing the frame
        `get_frame(t)` by another frame,  `image_func(get_frame(t))`
        """
        return self.fl(lambda gf, t: image_func(gf(t)), apply_to)

    #--------------------------------------------------------------
    # C O M P O S I T I N G

    
    def blit_on(self, picture, t):
        """
        Returns the result of the blit of the clip's frame at time `t`
        on the given `picture`, the position of the clip being given
        by the clip's ``pos`` attribute. Meant for compositing.
        """

        hf, wf = sizef = picture.shape[:2]

        if self.ismask and picture.max() != 0:
                return np.maximum(picture,
                                  self.blit_on(np.zeros(sizef), t))

        ct = t - self.start  # clip time

        # GET IMAGE AND MASK IF ANY

        img = self.get_frame(ct)
        mask = (None if (self.mask is None) else
                self.mask.get_frame(ct))
        hi, wi = img.shape[:2]

        # SET POSITION

        pos = self.pos(ct)


        # preprocess short writings of the position
        if isinstance(pos,str):
            pos = { 'center': ['center','center'],
                    'left': ['left','center'],
                    'right': ['right','center'],
                    'top':['center','top'],
                    'bottom':['center','bottom']}[pos]
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

    def add_mask(self, constant_size=True):
        """ Add a mask VideoClip to the VideoClip.

        Returns a copy of the clip with a completely opaque mask
        (made of ones). This makes computations slower compared to
        having a None mask but can be useful in many cases. Choose

        Set ``constant_size`` to  `False` for clips with moving
        image size.
        """
        if constant_size:
            mask = ColorClip(self.size, 1.0, ismask=True)
            return self.set_mask( mask.set_duration(self.duration))
        else:
            get_frame = lambda t: np.ones(self.get_frame(t).shape)
            mask = VideoClip(ismask=True, get_frame = get_frame)
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
          Position of the clip in the final clip.

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
            colorclip = colorclip.set_opacity(col_opacity)

        if self.duration is not None:
            colorclip = colorclip.set_duration(self.duration)

        result = CompositeVideoClip([colorclip, self.set_pos(pos)],
                                  transparent=(col_opacity != None))

        return result


    @outplace
    def set_get_frame(self, gf):
        """ Change the clip's ``get_frame``.

        Returns a copy of the VideoClip instance, with the get_frame
        attribute set to `gf`.
        """
        self.get_frame = gf
        self.size = gf(0).shape[:2][::-1]


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
    def set_pos(self, pos, relative=False):
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



    def to_ImageClip(self,t=0):
        """
        Returns an ImageClip made out of the clip's frame at time ``t``
        """
        return ImageClip(self.get_frame(t))



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
            newclip = self.fl_image( f )
            newclip.ismask = False
            return newclip
        else:
            return self


    @requires_duration
    def iter_frames(self, fps=None):
        """ Iterates over all the frames of the clip.
        
        Returns each frame of the clip as a HxWxN np.array,
        where N=1 for mask clips and N=3 for RGB clips.
        
        This function is not really meant for video editing.
        It provides an easy way to do frame-by-frame treatment of
        a video, for fields like science, computer vision...
        
        The ``fps`` (frames per second) parameter is optional if the
        clip already has a ``fps`` attribute.
        
        Examples
        ---------
        
        >>> # prints the maximum of red that is contained
        >>> # on the first line of each frame of the clip.
        >>> from moviepy.editor import VideoFileClip
        >>> myclip = VideoFileClip('myvideo.mp4')
        >>> for frame in myclip.iter_frames():
        >>>     print ( frame[0,:,0].max() )
        
        """
        
        if fps is None:
            fps = self.fps
            
        for t in np.arange(0, self.duration, 1.0/fps):
            yield self.get_frame(t)

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
                 fromalpha=False):

        VideoClip.__init__(self, ismask=ismask)

        if isinstance(img, str):
            img = ffmpeg_read_image(img,with_mask=transparent)

        if len(img.shape) == 3: # img is (now) a RGB(a) numpy array

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
        self.get_frame = lambda t: img
        self.size = img.shape[:2][::-1]
        self.img = img




    def fl(self, fl,  apply_to=[], keep_duration=True):
        """ General transformation filter.

        Equivalent to VideoClip.fl . The result is no more an
        ImageClip, it has the class VideoClip (since it may be animated)
        """

        # When we use fl on an image clip it may become animated.
        #Therefore the result is not an ImageClip, just a VideoClip.
        newclip = VideoClip.fl(self,fl, apply_to=apply_to,
                               keep_duration=keep_duration)
        newclip.__class__ = VideoClip
        return newclip



    @outplace
    def fl_image(self, image_func, apply_to= []):
        """ Image-transformation filter.

        Does the same as VideoClip.fl_image, but for ImageClip the
        tranformed clip is computed once and for all at the beginning,
        and not for each 'frame'.
        """

        arr = image_func(self.get_frame(0))
        self.size = arr.shape[:2][::-1]
        self.get_frame = lambda t: arr
        self.img = arr

        for attr in apply_to:
            if hasattr(self, attr):
                a = getattr(self, attr)
                if a != None:
                    new_a =  a.fl_image(image_func)
                    setattr(newclip, attr, new_a)



    @outplace
    def fl_time(self, time_func, apply_to =['mask', 'audio']):
        """ Time-transformation filter.

        Applies a transformation to the clip's timeline
        (see Clip.fl_time).

        This method does nothing for ImageClips (but it may affect their
        masks of their audios). The result is still an ImageClip.
        """

        for attr in apply_to:
            if hasattr(self, attr):
                a = getattr(self, attr)
                if a != None:
                    new_a = a.fl_time(time_func)
                    setattr(self, attr, new_a)



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


    def __init__(self,size, col=(0, 0, 0), ismask=False):
        w, h = size
        shape = (h, w) if np.isscalar(col) else (h, w, len(col))
        ImageClip.__init__(self, np.tile(col, w * h).reshape(shape),
                           ismask=ismask)



class TextClip(ImageClip):

    """ Class for autogenerated text clips.

    Creates an ImageClip originating from a script-generated text image.
    Requires ImageMagick.

    Parameters
    -----------

    txt
      either a string, or a filename. If txt is in a file and
      whose name is ``mytext.txt`` for instance, then txt must be
      equal to ``@mytext.txt`` .

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



    def __init__(self, txt, size=None, color='black',
             bg_color='transparent', fontsize=None, font='Courier',
             stroke_color=None, stroke_width=1, method='label',
             kerning=None, align='center', interline=None,
             tempfilename=None, temptxt=None,
             transparent=True, remove_temp=True,
             print_cmd=False):

        if not txt.startswith('@'):
            if temptxt is None:
                temptxt_fd, temptxt = tempfile.mkstemp(suffix='.txt')
                os.write(temptxt_fd, txt)
                os.close(temptxt_fd)
            txt = '@'+temptxt
        else:
            txt = "'%s'"%txt

        if size != None:
            size = ('' if size[0] is None else str(size[0]),
                    '' if size[1] is None else str(size[1]))

        cmd = ( [IMAGEMAGICK_BINARY,
               "-background", bg_color,
               "-fill", color,
               "-font", font])

        if fontsize !=None:
            cmd += ["-pointsize", "%d"%fontsize]
        if kerning != None:
            cmd += ["-kerning", "%0.1f"%kerning]
        if stroke_color != None:
            cmd += ["-stroke", stroke_color, "-strokewidth",
                                             "%.01f"%stroke_width]
        if size != None:
            cmd += ["-size", "%sx%s"%(size[0], size[1])]
        if align != None:
            cmd += ["-gravity",align]
        if interline != None:
            cmd += ["-interline-spacing", "%d"%interline]

        if tempfilename is None:
            tempfile_fd, tempfilename = tempfile.mkstemp(suffix='.png')
            os.close(tempfile_fd)

        cmd += ["%s:%s" %(method, txt),
        "-type",  "truecolormatte", "PNG32:%s"%tempfilename]

        if print_cmd:
            print( " ".join(cmd) )

        subprocess_call(cmd, verbose=False )

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
        """
        Returns the list of all valid entries for the argument given
        (can be ``font``, ``color``, etc...) argument of ``TextClip``
        """
        process = subprocess.Popen([IMAGEMAGICK_BINARY, '-list', arg],
                                   stdout=subprocess.PIPE)
        result = process.communicate()[0]
        lines = result.splitlines()

        if arg == 'font':
            return [l[8:] for l in lines if l.startswith("  Font:")]
        elif arg == 'color':
            return [l.split(" ")[1] for l in lines[2:]]
