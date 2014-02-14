"""
This module implements VideoClip (base class for video clips) and its
main subclasses:
- Animated clips:     VideofileClip, DirectoryClip
- Static image clips: ImageClip, ColorClip, TextClip,
"""

import time
import os
import sys
import subprocess
import multiprocessing
import threading
from copy import copy
from tqdm import tqdm


import numpy as np

from moviepy.decorators import  apply_to_mask, requires_duration

import moviepy.audio.io as aio
import moviepy.video.io.ffmpeg_writer as ffmpeg_writer
import moviepy.video.io.ffmpeg_reader as ffmpeg_reader
import moviepy.video.io.ffmpeg_tools as ffmpeg_tools

from  moviepy.video.tools.drawing import blit
from moviepy.Clip import Clip
from moviepy.conf import FFMPEG_BINARY




class VideoClip(Clip):

    """
    
    Base class for video clips. See ``VideofileClip``, ``ImageClip`` etc. for
    more user-friendly classes. 
    
    :param ismask: `True` if the clip is going to be used as a mask.
    
    :ivar size: the size of the clip, (width,heigth), in pixels.
    :ivar w: te width of the clip, in pixels.
    :ivar h: te height of the clip, in pixels.
    
    
    :ivar get_frame: A function ( t-> frame at time t )
    
    :ivar mask: VideoClip mask attached to this clip. If mask is ``None``,
                The video clip is fully opaque.
                
    :ivar audio: A :class:AudioClip attached to the video clip.
    
    :ivar pos: a function ``t->(x,y)`` where ``x,y`` is the position
               in pixels of the clip when it is composed with other clips.
               See ``VideoClip.set_pos``
               
    :ivar relative_pos: see variable ``pos``.
    
    :ivar ismask: Boolean set to `True` if the clip is a mask.
    

    """

    def __init__(self, ismask=False):
        Clip.__init__(self)
        self.mask = None
        self.audio = None
        self.pos = lambda t: (0, 0)
        self.relative_pos = False
        self.ismask = ismask

    @property
    def w(self):
        return self.size[0]

    @property
    def h(self):
        return self.size[1]

    def save_frame(self, filename, t=0, savemask=False):
        """ 
        Saves the frame of clip corresponding to time ``t`` in
        'filename'. If ``savemask`` is ``True`` the mask is saved in the
        alpha layer of the picture.
        """
        im = self.get_frame(t)
        if savemask and self.mask is not None:
            mask = 255 * self.mask.get_frame(t)
            im = np.dstack([im, mask]).astype('uint8')
        ffmpeg_writer.write_image(filename, im)

    @requires_duration
    def to_directory(self, foldername, fps, transparent=True,
                     overwrite=True, startFrame=0):
        """
        Writes the frames of the clip into a folder as png format,
        and returns the :class:DirectoryClip associated with this
        folder
        
        :param foldername: name of the folder (what did you expect ?)
        
        :param fps: Number of frames per second of movie.
        
        :param transparent: If `True`, the png images generated will
            possess an alpha layer representing the mask of the clip.
            
        :param overwrite: If `True`, will overwrite the content of
            `folder` if already existing.
            
        :param startFrame: Useless for the moment, but may come in handy
            once parallelization is implemented.
        
        """
        print( "writing frames in [%s]" % foldername )

        try:
            os.mkdir(foldername)
        except:
            if not overwrite:
                print( "Error: Maybe set overwrite =true ")

        tt = np.arange(0, self.duration, 1.0 / fps)
        tt_feedback = tt[::len(tt) / 10]

        for i, t in tqdm(list(enumerate(tt))[startFrame:]):

            picname = "%s/%s%06d.png" % (foldername, foldername, i)
            pic = self.get_frame(t)
            if transparent and (self.mask is not None):
                fmask = self.mask.get_frame(t)
                pic = np.dstack([pic, 255 * fmask]).astype('uint8')
            imsave(picname, pic)

        print( "done." )
        return DirectoryClip(foldername, fps=fps)



    def to_videofile(self, filename, fps=24, codec='libx264',
                 bitrate=None, audio=True, audio_fps=44100, 
                 audio_nbytes = 2, audio_codec= 'libvorbis',
                 audio_bitrate = None, audio_bufsize = 40000,
                 temp_audiofile=None,
                 rewrite_audio = True, remove_temp = True,
                 para = True, verbose = True):
        """
        Makes a video file out of the clip.
        First the clip is transformed into a directory clip, which means
        that the frames of the future movie are computed and stored in a
        folder as png files.
        Then a ``DirectoryClip`` is made out of this folder and
        transformed into a movie using ffmpeg (see DirectoryClip.to_videofile) 
        
        Returns the directory clip.
        
        :param filename: name of the video file. Whatever the codec used,
            it is best to write the movie name as .avi
            
        :param fps: Frames per second in the final movie.
        
        :param codec: Codec to use for image encoding. Can be 
            - 'rawvideo','png' : will produce a raw video, of perfect quality,
            but possibly very huge size. 'png' is still lossless but produces
            smaller files.
            - 'mpeg4' : For nice quality, very well compressed videos.
            - 'libx264' : A little better than 'mpeg4', a little heavier.
            - Any of the (many) other codec supported by ffmpeg.
            
        :param audio: Either ``True``, ``False``, or a file name.
            If ``True`` and the clip has an audio clip attached, this
            audio clip will be incorporated as a soundtrack in the movie.
            If ``audio`` is the name of a .wav file, this wav file will
            be incorporated as a soundtrack in the movie.
        
        :param audiofps: frame rate to use when writing the sound.
          
        :param temp_wav: the name of the temporary audiofile to be
             generated and incorporated in the the movie, if any.
        
        """
        
        if audio_codec == 'raw16':
            audio_codec = 'pcm_s16le'
        elif audio_codec == 'raw32':
            audio_codec = 'pcm_s32le'
        
        if verbose:
            def verbose_print(s):
                sys.stdout.write(s)
                sys.stdout.flush()
        else:
            verbose_print = lambda *a : None
        
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
                
                # make a name for the temporary file
                
                D_ext = {'libmp3lame': 'mp3',
                       'libvorbis':'ogg',
                       'libfdk_aac':'m4a',
                       'pcm_s16le':'wav',
                       'pcm_s32le': 'wav'}
                
                if audio_codec in D_ext.values():
                    ext = audio_codec
                else:
                    if audio_codec in D_ext.keys():
                        ext = D_ext[audio_codec]
                    else:
                        raise ValueError('audio_codec for file'
                                          '%d unkown !'%filename)
                    
                temp_audiofile = (Clip._TEMP_FILES_PREFIX +
                            "to_videofile_SOUND." + ext)
            
            make_audio = ( (not os.path.exists(temp_audiofile)) 
                            or rewrite_audio)
            merge_audio = True
            
        else:
            
            make_audio = False
            merge_audio = False
        
        if merge_audio:
            
            name, ext = os.path.splitext(os.path.basename(filename))
            videofile = Clip._TEMP_FILES_PREFIX + "to_videofile" + ext
            
        else:
            
            videofile = filename
            
        # enough cpu for multiprocessing ?
        enough_cpu = (multiprocessing.cpu_count() > 2)
        
        verbose_print("Making file %s ...\n"%filename)
        
        if para and make_audio and  enough_cpu:
            # Parallelize
            verbose_print("Writing audio/video in parrallel.\n")
            audioproc = multiprocessing.Process(
                    target=self.audio.to_audiofile,
                    args=(temp_audiofile,audio_fps,audio_nbytes,
                          audio_bufsize,audio_codec, audio_bitrate,verbose))
            audioproc.start()
            ffmpeg_writer.ffmpeg_write(self,  videofile, fps, codec,
                         bitrate=bitrate, verbose=verbose)
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
            ffmpeg_writer.ffmpeg_write(self, videofile, fps, codec,
                                       bitrate=bitrate, verbose=verbose)
        
        # Merge with audio if any and trash temporary files.
        if merge_audio:
            
            verbose_print("\nNow merging video and audio...\n")
            ffmpeg_tools.merge_video_audio(videofile,temp_audiofile,
                                  filename, ffmpeg_output=True)
                                  
            if remove_temp:
                os.remove(videofile)
                if not isinstance(audio,str):
                    os.remove(temp_audiofile)
            verbose_print("\nYour video is ready ! Fingers crossed"+
                          " for the Oscars !")
                
                
    def blit_on(self, picture, t):
        """ Returns the result of the blit of the clip's frame at time `t`
            on the given `picture`, the position of the clip being given
            by the clip's ``pos`` attribute. Meant for compositing.  """

        hf, wf = sizef = picture.shape[:2]

        if self.ismask and picture.max() != 0:
                return np.maximum(picture, self.blit_on(np.zeros(sizef), t))

        ct = t - self.start  # clip time
        
        # GET IMAGE AND MASK IF ANY
        
        img = self.get_frame(ct)
        mask = (None if (self.mask is None) else self.mask.get_frame(ct))
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
        
        
        
    def to_gif(self, filename, fps=None, program= 'ImageMagick',
            opt="OptimizeTransparency", fuzz=1, verbose=True,
            loop=0, dispose=False):
        """
        Converts a VideoClip into an animated GIF using ImageMagick or
        ffmpeg.
        :param clip: the VideoClip to be converted.
        :param filename: name of the gif, like 'myAnimation.gif'
        :param fps: number of frames per second (see note below). If it
            isn't provided, then the function will look for the clip's
            ``fps`` attribute (VideoFileClip, for instance, have one).
        :param program: software to use for the conversion, either
            'ImageMagick' or 'ffmpeg'.
        :param opt: (ImageMagick only) optimalization to apply, either
            'optimizeplus' or 'OptimizeTransparency'.
        :param fuzz: (ImageMagick only) Compresses the GIF by considering
            that the colors that are less than fuzz% different are in fact
            the same.
        
        
        *Note:* The gif will be playing the clip in real time (you can
        only change the frame rate). If you want the gif to be slower
        than the clip you will write
            
            >>> # slow down clip 50% and make it a gif
            >>> myClip.speedx(0.5).
        
        """
        
        def verboseprint(s):
            if verbose: print( "MoviePy: " + s )
        
        if fps is None:
            fps = self.fps
        
        fileName, fileExtension = os.path.splitext(filename)
        tt = np.arange(0,self.duration, 1.0/fps)
        tempfiles = []
        
        verboseprint( "Generating GIF frames" )
        
        for i, t in enumerate(tt):
            
            name = "%s_TEMP%04d.png"%(fileName,i+1)
            tempfiles.append(name)
            self.save_frame(name, t, savemask=True)
            
        delay = int(100.0/fps)
        
        if program == "ImageMagick":
            
            cmd = ("convert -delay %d"%delay +
                  " -dispose %d"%(2 if dispose else 1)+
                  " -loop %d"%loop+
                  " `seq -f %s"%fileName +"_TEMP%04g.png"+
                  " 1 1 %d`"%len(tt) +
                  " -coalesce -fuzz %02d"%fuzz + "%"+
                  " -layers %s %s"%(opt,filename))
            os.system(cmd)
            
        elif program == "ffmpeg":
            
            cmd = [FFMPEG_BINARY,'-y', '-f', 'image2',
                   '-i', fileName+'_TEMP%04d.png',
                   '-r',str(fps),
                   filename]
                   
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            proc.wait()
            print( proc.stderr )
            
        for f in tempfiles:
            os.remove(f)
        
        verboseprint('GIF generated !')

    #-----------------------------------------------------------------
    # F I L T E R I N G
    
    
    def subfx(self, fx, ta=0, tb=None, **kwargs):
        """
        Returns a new clip in which the function ``fun`` (clip->clip) has
        been applied to the subclip between times `ta` and `tb` (in
        seconds).
        
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
    
    def fl_image(self, image_func, applyto=[]):
        """ Modifies the images of a clip by replacing the frame
            `get_frame(t)` by another frame,  `image_func(get_frame(t))`
        """
        return self.fl(lambda gf, t: image_func(gf(t)), applyto)

    #--------------------------------------------------------------
    # C O M P O S I T I N G
    
    
    def add_mask(self, constant_size=True):
        """ 
        Returns a copy of the clip with a completely opaque mask
        (made of ones). This makes computations slow compared to having
        a None mask but can be useful in many cases. Choose
        
        :param constant_size: `False` for clips with moving image size.
        """
        if constant_size:
            mask = ColorClip(self.size, 1.0, ismask=True)
            return self.set_mask( mask.set_duration(self.duration))
        else:
            mask = VideoClip(ismask=True).set_get_frame(
                lambda t: np.ones(self.get_frame(t).shape))
            return self.set_mask(mask.set_duration(self.duration))
            
    def on_color(self, size=None, color=(0, 0, 0), pos=None,
                 col_opacity=None):
        """ 
        Returns a clip made of the current clip overlaid on a color
        clip of a possibly bigger size. Can serve to flatten transparent
        clips
        
        :param size: size of the final clip. By default it will be the
           size of the current clip.
        :param bg_color: the background color of the final clip
        :param pos: the position of the clip in the final clip.
        :param col_opacity: should the added zones be transparent ?
        """
        from compositing.CompositeVideoClip import CompositeVideoClip
        if size is None:
            size = self.size
        if pos is None:
            pos = 'center'
        colorclip = ColorClip(size, color)
        if col_opacity:
            colorclip = colorclip.set_opacity(col_opacity)
            
        if self.duration != None:
            colorclip = colorclip.set_duration(self.duration)

        result = CompositeVideoClip([colorclip, self.set_pos(pos)],
                                  transparent=(col_opacity != None))
                                  
        return result
    
    
    def set_get_frame(self, gf):
        newclip = Clip.set_get_frame(self, gf)
        newclip.size = newclip.get_frame(0).shape[:2][::-1]
        return newclip

    def set_audio(self, audioclip):
        """ Returns a copy of the clip with the audio set to ``audio``,
            which must be a VideoClip. """
        newclip = copy(self)
        newclip.audio = audioclip
        return newclip

    def set_mask(self, mask):
        """ Returns a copy of the clip with the mask set to ``mask``,
            which must be a greyscale (values in 0-1) VideoClip"""
        newclip = copy(self)
        newclip.mask = mask
        return newclip

    def set_opacity(self, op):
        """
        Returns a semi-transparent copy of the clip where the mask is
        multiplied by ``op`` (any float, normally between 0 and 1).
        """
        newclip = copy(self)
        
        if not newclip.mask:
            newclip = newclip.add_mask()
            
        newclip.mask = newclip.mask.fl_image(lambda pic: op * pic)
        return newclip

    @apply_to_mask
    def set_pos(self, pos, relative=False):
        """ 
        Sets the position that the clip will have when included
        in compositions. The argument ``pos`` can be either a couple
        ``(x,y)`` or a function ``t-> (x,y)``. `x` and `y` mark the
        location of the top left corner of the clip, and can be
        of several types:
        
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

        newclip = copy(self)
        newclip.relative_pos = relative
        if hasattr(pos, '__call__'):
            newclip.pos = pos
        else:
            newclip.pos = lambda t: pos

        return newclip

    #--------------------------------------------------------------
    # CONVERSIONS
    
    def to_ImageClip(self,t=0):
        """
        Return an ImageClip made out of the clip's frame at time ``t``
        """
        return ImageClip(self.get_frame(t))
        
    def to_mask(self, canal=0):
        """ Returns a mask a video clip made from the clip. """
        if self.ismask:
            return self
        else:
            newclip = self.fl_image(lambda pic: 1.0 * pic[:, :, canal] / 255)
            newclip.ismask = True
            return newclip

    def to_RGB(self):
        """
        Returns a non-mask video clip made from the mask video clip.
        """
        if self.ismask:
            newclip = self.fl_image(
                lambda pic: np.dstack(3 * [255 * pic]).astype('uint8'))
            newclip.ismask = False
            return newclip
        else:
            return self


    #----------------------------------------------------------------
    # Audio
    
    def without_audio(self):
        """ Returns a copy of the clip with audio set to None. """
        newclip = copy(self)
        newclip.audio = None
        return newclip
    
    def afx(self, fun, *a, **k):
        """
        Returns a new clip whose audio has been transformed by ``fun``.
        """
        newclip = self.copy()
        newclip.audio = newclip.audio.fx(fun, *a, **k)
        return newclip 
        
    #-----------------------------------------------------------------
    # Previews:

try:
    # Add methods preview and show (only if pygame installed)
    from moviepy.video.io.preview import show, preview
    VideoClip.preview = preview
    VideoClip.show = show
except:
    pass





"""---------------------------------------------------------------------

    ImageClip (base class for all 'static clips') and its subclasses
    ColorClip and TextClip.
    I would have liked to put these in a separate file but Python is bad
    at cyclic imports.

---------------------------------------------------------------------"""



class ImageClip(VideoClip):

    """
    
    A video clip originating from a picture. This clip will simply
    display the given picture at all times. For instance:
    
    >>> clip = ImageClip("myHouse.jpeg")
    >>> clip = ImageClip( someArray ) # a Numpy array represent
    
    :param img: Any picture file (png, tiff, jpeg, etc.) or any array
         representing an RGB image (for instance a frame from a VideoClip
         or a picture read with scipy of skimage's imread method).
         
    :param ismask: `True` if the clip is a mask.
    :param transparent: `True` (default) if you want the alpha layer
         of the picture (if it exists) to be used as a mask.
    
    :ivar img: array representing the image of the clip.
        
    """

    def __init__(self, img, ismask=False, transparent=True, fromalpha=False):

        VideoClip.__init__(self, ismask=ismask)

        if isinstance(img, str):
            img = ffmpeg_reader.read_image(img,with_mask=transparent)
        
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
        
        # if the image was just a 2D mask, it should arrive here unchanged
        self.get_frame = lambda t: img
        self.size = img.shape[:2][::-1]
        self.img = img
    
    def fl(self, fl,  applyto=[], keep_duration=True):
        """ 
        Equivalent to VideoClip.fl . The result is no more an
        ImageClip, it has the class VideoClip (as it may be animated)
        """
        # When we use fl on an image clip it may become animated.
        #Therefore the result is not an ImageClip, just a VideoClip.
        newclip = VideoClip.fl(self,fl, applyto=applyto,
                               keep_duration=keep_duration)
        newclip.__class__ = VideoClip
        return newclip
    
    def fl_image(self, image_func, applyto= []):
        """
        Similar to VideoClip.fl_image, but for ImageClip the
        tranformed clip is computed once and for all at the beginning,
        and not for each 'frame'.
        """
            
        newclip = self.copy()
        arr = image_func(self.get_frame(0))
        newclip.size = arr.shape[:2][::-1]
        newclip.get_frame = lambda t: arr
        newclip.img = arr
        
        for attr in applyto:
            if hasattr(newclip, attr):
                a = getattr(newclip, attr)
                if a != None:
                    setattr(newclip, attr, a.fl_image(image_func))
                    
        return newclip
    
    def fl_time(self, timefun, applyto =['mask', 'audio']):
        """
        This method does nothing for ImageClips (but it may affect their
        masks of their audios). The result is still an ImageClip
        """
        newclip = self.copy()
        
        for attr in applyto:
            if hasattr(newclip, attr):
                a = getattr(newclip, attr)
                if a != None:
                    setattr(newclip, attr, a.fl_image(image_func))
        
        return newclip



class ColorClip(ImageClip):
    """
    An ImageClip showing just one color.
    
    :param size: Size (width, height) in pixels of the clip
    
    :param color: If argument ``ismask`` is False, ``color`` indicates
      the color in RGB of the clip (default is black). If `ismask``
      is True, ``color`` must be  a float between 0 and 1 (default is 1) 
      
    :param ismask: Is the clip a mask clip ?
    
    """
    def __init__(self,size, col=(0, 0, 0), ismask=False):
        w, h = size
        shape = (h, w) if np.isscalar(col) else (h, w, len(col))
        ImageClip.__init__(self, np.tile(col, w * h).reshape(shape),
                           ismask=ismask)



class TextClip(ImageClip):

    """ 
    
    An image clip originating from a script-generated text image.
    Makes a text PNG using ImageMagick.
    
    :param txt: either a string, or a filename. If txt is in a file and
         whose name is ``mytext.txt`` for instance, then txt must be
         equal to ``@mytext.txt`` .
         
    :param size: Size of the picture in pixels. Can be auto-set if
         method='label', but mandatory if method='caption'.
         the height can be None, it will then be auto-determined.
    
    :param bg_color: Color of the background. See ``TextClip.list('color')``
         for a list of acceptable names.
    
    :param color: Color of the background. See ``TextClip.list('color')``
        for a list of acceptable names.
    
    :param font: Name of the font to use. See ``TextClip.list('font')`` for
        the list of fonts you can use on your computer.
       
    :param stroke_color: Color of the stroke (=contour line) of the text.
        if ``None``, there will be no stroke.
       
    :param stroke_width: Width of the strocke, in pixels. Can be a float,
        like 1.5.
       
    :param method: 'label' (the picture will be autosized so as to fit
        exactly the size) or 'caption' (the text will be drawn in a picture
        with fixed size provided with the ``size`` argument). If `caption`,
        the text will be wrapped automagically (sometimes it is buggy, not
        my fault, complain to the ImageMagick crew) and can be aligned or
        centered (see parameter ``align``).
    
    :param kerning: Changes the default spacing between letters. For
       instance ``kerning=-1`` will make the letters 1 pixel nearer from
       each other compared to the default spacing. 
    
    :param align: center | East | West | South | North . Will work if
        ``method`` is set to ``caption``
    
    :param transparent: ``True`` (default) if you want to take into account
        the transparency in the image.
    
    """

    def __init__(self, txt, size=None, color='black', bg_color='transparent',
             fontsize=None, font='Courier',
             stroke_color=None, stroke_width=1, method='label',
             kerning=None, align='center', interline=None,
             tempfile='temp.png',
             temptxt='temp.txt', transparent=True, remove_temp=True,
             print_cmd=False):

        if not txt.startswith('@'):
            temptxt = 'temp.txt'
            with open(temptxt, 'w+') as f:
                f.write(txt)
            txt = '@temp.txt'
        else:
            txt = "'%s'"%txt

        if size != None:
            size = ('' if size[0] is None else str(size[0]),
                    '' if size[1] is None else str(size[1]))

        cmd = ( ["convert",
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
            
        cmd += ["%s:%s" %(method, txt),
        "-type",  "truecolormatte", "PNG32:%s"%tempfile]
        
        if print_cmd:
            print( " ".join(cmd) )

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        proc.wait()
        if proc.returncode:
            print ("Error: problem in the generation of the text file"+
                "by ImageMagick. Certainly wrong arguments in TextClip")
        
        ImageClip.__init__(self, tempfile, transparent=transparent)
        self.txt = txt
        self.color = color
        self.stroke_color = stroke_color

        if remove_temp:
            os.remove(tempfile)
            try:
                os.remove(temptxt)
            except:
                pass

    @staticmethod
    def list(arg):
        """ Returns the list of all valid entries for the argument given
        (can be ``font``, ``color``, etc...)
        argument of ``TextClip`` """
        process = subprocess.Popen(['convert', '-list', arg],
                                   stdout=subprocess.PIPE)
        result = process.communicate()[0]
        lines = result.splitlines()

        if arg == 'font':
            return [l[8:] for l in lines if l.startswith("  Font:")]
        elif arg == 'color':
            return [l.split(" ")[1] for l in lines[2:]]
