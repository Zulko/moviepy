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


import numpy as np

from moviepy.decorators import  apply_to_mask, requires_duration

import moviepy.audio.io as aio
import io.ffmpeg as ffmpeg
import io as vio
import ImageClip as ImClip
from moviepy.Clip import Clip
from tools.drawing import blit



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
        if savemask:
            mask = 255 * self.mask.get_frame(t)
            im = np.dstack([im, mask]).astype('uint8')
        write_image(filename, im)

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
        print "writing frames in [%s]" % foldername,

        try:
            os.mkdir(foldername)
        except:
            if not overwrite:
                print "Error: Maybe set overwrite =true "

        tt = np.arange(0, self.duration, 1.0 / fps)
        tt_feedback = tt[::len(tt) / 10]

        for i, t in list(enumerate(tt))[startFrame:]:

            picname = "%s/%s%06d.png" % (foldername, foldername, i)
            pic = self.get_frame(t)
            if transparent and (self.mask is not None):
                fmask = self.mask.get_frame(t)
                pic = np.dstack([pic, 255 * fmask]).astype('uint8')
            imsave(picname, pic)
            if t in tt_feedback:
                print "%d" % (int(100 * t / tt[-1])) + "%",

        print "done."
        return DirectoryClip(foldername, fps=fps)



    def to_videofile(self, filename, fps=24, codec='libx264',
                 bitrate=None, audio=True, audio_fps=44100,
                 audio_nbytes = 2, audio_bufsize = 40000, temp_wav=None,
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
        
        if verbose:
            def verbose_print(s):
                sys.stdout.write(s)
                sys.stdout.flush()
        else:
            verbose_print = lambda *a : None
        
        if isinstance(audio, str): 
            # audio is some audiofile it is maybe not a wav file. It is
            # NOT temporary file, it will NOT be removed at the end.
            temp_wav = audio
            make_audio = False
            merge_audio = True
            
        elif self.audio is None:
            # audio not provided as a file and no clip.audio
            make_audio = merge_audio =  False
            
        elif audio:
            # The audio will be the clip's audio
            if temp_wav is None:
                # make a name for the temporary folder
                temp_wav = Clip._TEMP_FILES_PREFIX + "to_videofile.wav"
            
            temp_wav = Clip._TEMP_FILES_PREFIX + "to_videofile.wav"
            make_audio = (not os.path.exists(temp_wav)) or rewrite_audio
            merge_audio = True
            
        else:
            
            make_audio = False
            merge_audio = False
        
        if merge_audio:
            name, ext = os.path.splitext(os.path.basename(filename))
            videofile = Clip._TEMP_FILES_PREFIX + "to_videofile" + ext
        else:
            videofile = filename
            
        
        enough_cpu = (multiprocessing.cpu_count() > 2)
        
        verbose_print("Making file %s ...\n"%filename)
        if para and make_audio and  enough_cpu:
            # Parallelize
            verbose_print("Writing audio/video in parrallel.\n")
            audioproc = multiprocessing.Process(
                    target=self.audio.to_audiofile,
                    args=(temp_wav,audio_fps,audio_nbytes,
                          audio_bufsize,verbose))
            audioproc.start()
            vio.ffmpeg_write(self,  videofile, fps, codec, bitrate=bitrate,
                         verbose=verbose)
            audioproc.join()
            if audioproc.exitcode:
                print ("WARNING: something went wrong with the audio"+
                       " writing, Exit code %d"%audioproc.exitcode)
        else:
            # Don't parallelize
            if make_audio:
                self.audio.to_audiofile(temp_wav,audio_fps, audio_nbytes,
                              audio_bufsize, verbose)
            vio.ffmpeg_write(self, videofile, fps, codec, verbose=verbose)
        
        # Merge with audio if any and trash temporary files.
        
        if merge_audio:
            
            verbose_print("\nNow merging video and audio...\n")
            vio.ffmpeg.merge_video_audio(videofile,temp_wav,filename,
                                     ffmpeg_output=False)
            if remove_temp:
                os.remove(videofile)
                if not isinstance(audio,str):
                    os.remove(temp_wav)
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

        clips = [c for c in left, center, right if c != None]
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
            return self.set_mask(ImClip.ColorClip(self.size, 1.0, ismask=True))
        else:
            mask = VideoClip(ismask=True).set_get_frame(
                lambda t: np.ones(self.get_frame(t).shape))
            return self.set_mask(mask)
            
    def on_color(self, size=None, color=(0, 0, 0), pos=None, col_opacity=None):
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
        colorclip = ImClip.ColorClip(size, color)
        if col_opacity:
            colorclip = colorclip.add_mask().set_opacity(col_opacity)

        return CompositeVideoClip([colorclip, self.set_pos(pos)],
                                  transparent=(col_opacity != None))
    
    
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
        newclip.mask = self.mask.fl_image(lambda pic: op * pic)
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
        return ImClip.ImageClip(self.get_frame(t))
        
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
        
    #-----------------------------------------------------------------
    # Previews:

try:
    # Add methods preview and show (only if pygame installed)
    from io.preview import show, preview
    VideoClip.preview = preview
    VideoClip.show = show
except:
    pass
