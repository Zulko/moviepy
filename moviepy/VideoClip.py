import time
import os
import shutil
import subprocess
from copy import copy

import numpy as np
from skimage.io import imread, imshow
import cv2
import pygame as pg
import ffmpeg

from Clip import Clip, apply_to_mask, requires_duration
from AudioClip import SoundClip, CompositeAudioClip

# Initiates a Pygame window
pg.init()
pg.display.set_caption('MoviePy')

#
#
#     TOOL FUNCTIONS
#
#


def imdisplay(imarray, screen=None):
    """ splashes the given image array on the given pygame screen """
    a = pg.surfarray.make_surface(imarray.swapaxes(0, 1))
    if screen == None:
        screen = pg.display.set_mode(imarray.shape[:2][::-1])
    screen.blit(a, (0, 0))
    pg.display.flip()



def blit(im1, im2, pos=[0, 0], mask=None, ismask=False):
    """
    Blits ``im1`` on ``im2`` as position ``pos=(x,y)``, using the
    ``mask`` if provided. If ``im1`` and ``im2`` are mask pictures
    (2D float arrays) then ``ismask`` must be ``True``
    """

    # xp1,yp1,xp2,yp2 = blit area on im2
    # x1,y1,x2,y2 = area of im1 to blit on im2
    xp, yp = pos
    x1 = max(0, -xp)
    y1 = max(0, -yp)
    h1, w1 = im1.shape[:2]
    h2, w2 = im2.shape[:2]
    xp2 = min(w2, xp + w1)
    yp2 = min(h2, yp + h1)
    x2 = min(w1, w2 - xp)
    y2 = min(h1, h2 - yp)
    xp1 = max(0, xp)
    yp1 = max(0, yp)

    if (xp1 >= xp2) or (yp1 >= yp2):
        return im2

    blitted = im1[y1:y2, x1:x2]

    new_im2 = +im2

    if mask != None:
        mask = mask[y1:y2, x1:x2]
        if len(im1.shape) == 3:
            mask = np.dstack(3 * [mask])
        blit_region = new_im2[yp1:yp2, xp1:xp2]
        new_im2[yp1:yp2, xp1:xp2] = (
            1.0 * mask * blitted + (1.0 - mask) * blit_region)
    else:
        new_im2[yp1:yp2, xp1:xp2] = blitted

    return new_im2.astype('uint8') if (not ismask) else new_im2






class VideoClip(Clip):

    """
    
    Base class for video clips. See ``MovieClip``, ``ImageClip`` etc. for
    more user-friendly classes. 
    
    :param ismask: `True` if the clip is going to be used as a mask.
    
    :ivar size: the size of the clip, (width,heigth), in pixels.
    :ivar w: te width of the clip, in pixels.
    :ivar h: te height of the clip, in pixels.
    
    
    :ivar get_frame: A function `t-> frame at time t`
    
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
        # self.mask = (None if ismask else
        #        VideoClip(ismask=True).set_get_frame(lambda t:None))
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

    @requires_duration
    def preview(self, fps=15, audio=True, audiofps=22050):
        """ 
        Displays the clip in a window, at the given frames per second
        (of movie) rate. It will avoid that the clip be played faster
        than normal, but it cannot avoid the clip to be played slower
        than normal if the computations are complex. In this case, try
        reducing the ``fps``.
        
        :param fps: Number of frames per second to be displayed.
            
        :param audio: ``True`` (default) if you want the clip's audio
            to be played in playback. The synchronization is not garanteed.
            
        :param audiofps: The frames per second to use when generating the
             audio sound. The lower, the cheaper the sound will be.
        
        """

        if self.ismask:
            self = self.to_RGB()

        screen = pg.display.set_mode(self.size)

        if (audio == True) and (self.audio != None):
            self.audio.preview(fps=audiofps, sleep=False)
        
        img = self.get_frame(0)
        for t in np.arange(0, self.duration, 1.0 / fps):
            t1 = time.time()
            imdisplay(img, screen)
            img = self.get_frame(t)
            t2 = time.time()
            time.sleep(max(0, 1.0 / fps - (t2 - t1)))

    def show(self, t=0, with_mask=True):
        """
        Splashes the frame of clip corresponding to time ``t``.
        
        :param t: time in seconds of the frame to display.
        
        :param with_mask: ``False`` if the clip has a mask but you
             want to see the clip without the mask.
        
        """

        if self.ismask:
            self = self.to_RGB()
        if with_mask and (self.mask != None):
            self = CompositeVideoClip(self.size, [self])
        imdisplay(self.get_frame(t))

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
            
        cv2.imwrite(filename,im)

    def with_mask(self, constant_size=True):
        """ 
        Returns a copy of the clip with a completely opaque mask
        (made of ones). This makes computations slow compared to having
        a None mask but can be useful in many cases. Choose
        
        :param constant_size: `False` for clips with moving image size.
        """

        if constant_size:
            return self.set_mask(ColorClip(self.size, 1.0, ismask=True))
        else:
            mask = VideoClip(ismask=True).set_get_frame(
                lambda t: np.ones(self.get_frame(t).shape))
            return self.set_mask(mask)

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

    def to_movie(self, filename, fps=24, codec='DIVX',
                 audio=True, audiofps=44100, temp_wav='temp.wav',
                 remove_temp = True):
        """
        Makes a video file out of the clip.
        First the clip is transformed into a directory clip, which means
        that the frames of the future movie are computed and stored in a
        folder as png files.
        Then a ``DirectoryClip`` is made out of this folder and
        transformed into a movie using ffmpeg (see DirectoryClip.to_movie) 
        
        Returns the directory clip.
        
        :param filename: name of the video file. Whatever the codec used,
            it is best to write the movie name as .avi
            
        :param fps: Frames per second in the final movie.
        
        :param codec: Codec to use for image encoding. Can be 
            - 'raw' : will produce a raw video, of perfect quality, but
                      possibly very huge size.
            - 'DIVX' : For nice quality, very well compressed videos.
            - 'XVID' : A little better than 'DVIX', a little heavier.
            - Any of the (many) other codec supported by OpenCV, written
              as a string of four characters. See here for a list:
                  http://remisoft.ath.cx/article14/fourcc
            
        :param audio: Either ``True``, ``False``, or a file name.
            If ``True`` and the clip has an audio clip attached, this
            audio clip will be incorporated as a soundtrack in the movie.
            If ``audio`` is the name of a .wav file, this wav file will
            be incorporated as a soundtrack in the movie.
        
        :param audiofps: frame rate to use when writing the sound.
          
        :param temp_wav: the name of the temporary audiofile to be
             generated and incorporated in the the movie, if any.
        
        """
        
        print "Making file %s ..."%filename
        # Prepare audio
        
        if isinstance(audio, str):  # audio is a file
            temp_wav = audio
        elif self.audio is None:  # if audio not a file and no clip.audio
            audio = False
        elif audio:  # audio=True and clip.audio exists.
            print "Rendering audio.",
            self.audio.to_soundfile(temp_wav, audiofps)
        
        # If there is any audio we will need to first write a mute
        # temporary video file
        
        if audio:
            name, ext = os.path.splitext(filename)
            videofile = name + 'TEMP' + ext
        else:
            videofile = filename  
        
        # Write the movie
        print "Rendering video :",
        
        codec = 0 if (codec=='raw') else cv2.VideoWriter_fourcc(*codec)
        
        writer = cv2.VideoWriter(videofile, codec, fps, self.size)
        tt = np.arange(0, self.duration, 1.0/fps)
        lentt = len(tt)
        for i,t in enumerate(tt):
            writer.write(self.get_frame(t)[:,:,::-1].astype('uint8'))
            if i % (len(tt)/10) == 0:
                print "%d"%(100 * i / len(tt)) + "% ",
        writer.release()
        print "done !"
        
        # Merge with audio if any and trash temporary files.
        
        if audio:
            print "Now merging video and audio...",
            ffmpeg.merge_video_audio(videofile,temp_wav,filename)
            if remove_temp:
                os.remove(videofile)
                if not isinstance(audio,str):
                    os.remove(temp_wav)
            print "done !"
                
                
    def blit_on(self, picture, t):
        """ Returns the result of the blit of the clip's frame at time `t`
            on the given `picture` """

        hf, wf = sizef = picture.shape[:2]

        if self.ismask and picture.max() != 0:
                return np.maximum(picture, self.blit_on(np.zeros(sizef), t))

        ct = t - self.start  # clip time
        mask = (None if (self.mask is None) else self.mask.get_frame(ct))

        # Set position
        pos = list(self.pos(ct))
        img = self.get_frame(ct)

        hi, wi = img.shape[:2]

        # see set_pos doc for details
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
    
    
    def subapply(self, fun, ta=0, tb=None):
        """
        Returns a new clip in which the function ``fun`` (clip->clip) has
        been applied to the subclip between times `ta` and `tb` (in
        seconds).
        
        >>> # The scene between times t=3s and t=6s in ``clip`` will be
        >>> # be played twice slower in ``newclip``
        >>> newclip = clip.subapply(lambda c:c.speedx(0.5) , 3,6)
        
        """
        left = None if (ta == 0) else self.subclip(0, tb=ta)
        center = fun(self.subclip(ta, tb))
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

    @apply_to_mask
    def resize(self, newsize=None, height=None, width=None):
        """ 
        Returns a video clip that is a resized version of the clip.
        
        :param newsize: can be either ``(height,width)`` in pixels or
            a float representing a scaling factor.
                
        :param width: width of the new clip in pixel. The height is
            then computed so that the width/height ratio is conserved. 
                
        :param height: height of the new clip in pixel. The width is
            then computed so that the width/height ratio is conserved.
                 
        >>> myClip.resize( (460,720) ) # New resolution: (460,720)
        >>> myClip.resize(0.6) # width and heigth multiplied by 0.6
        >>> myClip.resize(width=800) # height computed automatically.
            
            
        """
        w, h = self.size

        if newsize != None:
            if isinstance(newsize, (int, float)):
                newsize = [newsize * w, newsize * h]
        elif height != None:
            newsize = [w * height / h, height]
        elif width != None:
            newsize = [width, h * width / w]
            
        newsize = map(int, newsize)[::-1]

        if self.ismask:
            fl = lambda pic: 1.0*cv2.resize((255 * pic).astype('uint8'),
                tuple(newsize[::-1]), interpolation=cv2.INTER_AREA)/255
        else:
            fl = lambda pic: cv2.resize(pic.astype('uint8'),
                tuple(newsize[::-1]), interpolation=cv2.INTER_AREA)

        return self.fl_image(fl)

    def on_color(self, size=None, color=(0, 0, 0), pos=None, col_opacity=None):
        """ Returns a clip made of the current clip overlaid on a color
            clip of bigger size.
        
        :param size: size of the final clip. By default it will be the
           size of the current clip.
        :param bg_color: the background color of the final clip
        :param pos: the position of the clip in the final clip.
        :param col_opacity: should the added zones be transparent ?
        """

        if size is None:
            size = self.size
        if pos is None:
            pos = ('center', 'center')
        colorclip = ColorClip(size, color)
        if col_opacity:
            colorclip = colorclip.with_mask().set_opacity(col_opacity)

        return CompositeVideoClip(size, [colorclip, self.set_pos(pos)],
                                  transparent=(col_opacity != None))

    @apply_to_mask
    def margin(self, mar=None, left=0, right=0, top=0,
               bottom=0, color=(0, 0, 0), opacity = 1.0):
        """
        Draws an external margin all around the frame.
        
        :param mar: if not ``None``, then the new clip has a margin of
            size ``mar`` in pixels on the left, right, top, and bottom.
            
        :param left, right, top, bottom: width of the margin in pixel
            in these directions.
            
        :param color: color of the margin.
        
        :param mask_margin: value of the mask on the margin. Setting
            this value to 0 yields transparent margins.
        
        """

        if (opacity != 1.0) and (self.mask is None) and not (self.ismask):
            self = self.with_mask()

        if mar != None:
            left = right = top = bottom = mar

        new_w, new_h = self.w + left + right, self.h + top + bottom

        if self.ismask:
            shape = (new_h, new_w)
            bg = np.tile(opacity, (new_h, new_w)).reshape(shape)
        else:
            shape = (new_h, new_w, 3)
            bg = np.tile(color, (new_h, new_w)).reshape(shape)

        def fl(pic):
            im = +bg
            im[top:top + self.h, left:left + self.w] = pic
            return im

        return self.fl_image(fl)

    def padded(self, size, color=(0, 0, 0)):
        """ internal margin by shrinking the frame """
        w, h = self.size
        return self.resize((x - 2 * size, y - 2 * size)).margin(size, color)

    def crop(self, x1=0, y1=0, x2=None, y2=None):
        if x2 is None:
            x2 = self.size[0]
        if y2 is None:
            y2 = self.size[1]
        return self.fl_image(lambda pic: pic[y1:y2, x1:x2],
                             applyto=['mask'])

    #--------------------------------------------------------------
    # C O M P O S I T I N G
    def set_get_frame(self, gf):
        newclip = Clip.set_get_frame(self, gf)
        newclip.size = newclip.get_frame(0).shape[:2][::-1]
        return newclip

    def set_audio(self, audioclip):
        """ mask must be a greyscale (0-1) Clip"""
        newclip = copy(self)
        newclip.audio = audioclip
        return newclip

    def set_mask(self, mask):
        """ mask must be a greyscale (0-1) Clip"""
        newclip = copy(self)
        newclip.mask = mask
        return newclip

    def set_opacity(self, op):
        """op is any float (normaly between 0 and 1) by which the
           clip's mask will be multiplied """
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

    def fadein(self, duration):
        """
        Makes the clip appear progressively, over ``duration`` seconds.
        Only works when the clip is include in a CompositeVideoClip.
        """
        newclip = copy(self)
        fading = lambda t: min(1.0 * t / duration, 1)
        fl = lambda gf, t: fading(t) * gf(t)
        newclip.mask = self.mask.fl(fl)
        return newclip

    @requires_duration
    def fadeout(self, duration):
        """
        Makes the clip disappear progressively, over ``duration`` seconds.
        Only works when the clip is include in a CompositeVideoClip.
        """
        newclip = copy(self)
        fading = lambda t: min(1.0 * (self.duration - t) / duration, 1)
        fl = lambda gf, t: fading(t) * gf(t)
        newclip.mask = self.mask.fl(fl)
        return newclip

    #--------------------------------------------------------------
    # CONVERSIONS
    def to_ImageClip(self):
        """ Return an ImageClip made out of the clip's first frame """
        return ImageClip(self.get_frame(0))

    def to_mask(self, canal=0):
        """ Returns a mask a video clip made from the clip. """
        if self.ismask:
            return self
        else:
            newclip = self.fl_image(lambda pic: 1.0 * pic[:, :, canal] / 255)
            newclip.ismask = True
            return newclip

    def to_RGB(self):
        """ Returns a non-mask video clip made from the mask video clip. """
        if self.ismask:
            newclip = self.fl_image(
                lambda pic: np.dstack(3 * [255 * pic]).astype('int'))
            newclip.ismask = False
            return newclip
        else:
            return self

    #----------------------------------------------------------------
    # Miscellaneous
    def manual_tracking(self, t1=None, t2=None, fps=5):
        """
        Allows manual tracking of an object in the video clip between
        times `t1` and `t2`. This displays the clip frame by frame
        and you must click on the object in each frame. If ``t2=None``
        only the frame at ``t1`` is taken into account.
        
        Returns a list [(t1,x1,y1),(t2,x2,y2) etc... ]
        
        >>> print myClip.manTrack(10, 13,fps=7)
        >>>
        >>> # To print 5 points coordinates at t=5 : 
        >>> for i in range(5):
        >>>     print myClip.manTrack(5)
        
        Tip: To avoid redoing the tracking each time you run your script,
        better save the result the first time and then load it at each run. 
        
        >>> # First time:
        >>> import pickle
        >>> txy = myClip.manTrack(20, 10,fps=10)
        >>> with open("chaplin_txy.dat",'w+') as f:
        >>>     pickle.dump(txy,f)
        >>>
        >>> # Next times:
        >>> import pickle
        >>> with open("chaplin_txy.dat",'r') as f:
        >>>     txy = pickle.load(txy,f)
        
        """

        screen = pg.display.set_mode(self.size)
        step = 1.0 / fps
        if (t1 is None) and (t2 is None):
            t1,t2 = 0, self.duration
        elif (t2 is None):
            t2 = t1 + step / 2
        t = t1
        txyList = []

        while t < t2:

            imdisplay(self.get_frame(t), screen)
            doContinue = True

            while doContinue:

                for event in pg.event.get():

                    if event.type == pg.KEYDOWN:
                        if (event.key == pg.K_BACKSLASH):
                            t -= step
                            txyList.pop()
                            doContinue = False

                    elif event.type == pg.MOUSEBUTTONDOWN:
                        x, y = pg.mouse.get_pos()
                        txyList.append((t, x, y))
                        doContinue = False
                        t += step

        return txyList


class MovieClip(VideoClip):

    """
    
    A video clip originating from a movie file. For instance:
    
    >>> clip = MovieClip("myHolidays.mp4")
    >>> clip2 = MovieClip("myMaskVideo.avi",ismask = True)
    
    :param source: Any video file: .ogv, .mp4, .mpeg, .avi, .mov etc.
    :param ismask: `True` if the clip is a mask.
    :param audio: If `True`, then the audio is extracted from the video
                  file, in wav format, and it attributed to the clip.
    
    :ivar source: Name of the original video file
    :ivar fps: Frames per second in the original file.
    :ivar nframes: Total number of frames in the original file.   
        
    """

    def __init__(self, source, ismask=False, audio=False):

        VideoClip.__init__(self, ismask)

        self.cap = cv2.VideoCapture(source)

        self.source = source

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

        self.nframes = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

        duration = 1.0 * (self.nframes) / self.fps
        self.duration = duration

        self.size = self.cap.read()[1].shape[:2][::-1]
        self.last_frame_read = 0

        def get_frame(t):
            """ 
            Gets the frame of the video at time t. Note for coders:
            getting an arbitrary frame in the video with opencv can be
            painfully slow if some decoding has to be made. This
            function tries to avoid fectching arbitrary frames whenever
            possible, by moving between adjacent frames.
            """

            nframe = int(self.fps * t)

            if nframe == self.last_frame_read:
                return self.cap.retrieve()[1][:, :, ::-1]
            elif (self.last_frame_read < nframe < (self.last_frame_read + 5)):
                for i in range(nframe - self.last_frame_read - 1):
                    self.cap.read()

            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, nframe - 1)

            frame = self.cap.read()[1]
            if frame is None:
                return self.last_frame
            else:
                self.last_frame_read = nframe
                frame = frame[:, :, ::-1]
                self.last_frame = frame
                return frame

        self.get_frame = get_frame

        if audio:
            temp = 'temp.wav'
            # try:
            ffmpeg.extract_audio(source, temp)
            self.audio = SoundClip(temp)
            os.remove(temp)
            # except:
            #    print "No audio detected in %s."%source


class DirectoryClip(VideoClip):

    """
    
    A VideoClip from a directory containing pictures
    
    """

    def __init__(self, source, fps, transparent=True, repeat=False, ismask=False):

        VideoClip.__init__(self, ismask=ismask)

        self.directory = source
        self.fps = fps
        self.pics = sorted(["%s/%s" % (source, f) for f in os.listdir(source)
                            if not f.endswith('.txt')])

        self.size = imread(self.pics[0]).shape[:2][::-1]

        if imread(self.pics[0]).shape[2] == 4:  # transparent png

            if ismask:
                def get_frame(t):
                    return 1.0 * imread(self.pics[int(self.fps * t)])[:, :, 3] / 255
            else:
                def get_frame(t):
                    return imread(self.pics[int(self.fps * t)])[:, :, :2]

            if transparent:
                self.mask = DirectoryClip(source, fps, ismask=True)

        else:

            def get_frame(t):
                return imread(self.pics[int(self.fps * t)])

        self.get_frame = get_frame
        self.duration = 1.0 * len(self.pics) / self.fps

    def to_movie(self, filename, bitrate=3000, audio=None):
        """
        Transforms the directory clip into a movie using ffmpeg.
        Uses the framerate specified by ``clip.fps``.
        
        :param filename: name of the video file to write in, like
            'myMovie.ogv' or 'myFilm.mp4'.
        :param bitrate: final bitrate of the video file (in kilobytes/s).
            3000-6000 gives generally light files and an acceptable quality.
        :param audio: the name of an audiofile to be incorporated in the
           the movie.
        """

        if audio != None:
            name, ext = os.path.splitext(filename)
            videofile = name + 'TEMP' + ext
        else:
            videofile = filename

        cmd = ("ffmpeg -y -f image2 -r %d -i %s/%s" % (
               self.fps, self.directory, self.directory) + "%06d.png" +
               " -b %dk -r %d %s" % (bitrate, self.fps, videofile))

        print "\nrunning:  %s" % cmd
        os.system(cmd)

        if audio != None:
            cmd = (" ffmpeg -y -i %s" % audio +
                   " -i %s -strict experimental %s" % (videofile, filename))
            print "running:  %s" % cmd
            os.system(cmd)
            os.remove(videofile)

class ImageClip(VideoClip):

    """
    
    A video clip originating from a picture. For instance:
    
    >>> clip = ImageClip("myHouse.jpeg")
    >>> clip = ImageClip( someNumpyArray )
    
    :param img: Any picture file (png, tif, jpeg, etc.) or any array
         representing an image, for instance a frame from a VideoClip
         or a picture read with scipy of skimage's imread method.
         
    :param ismask: `True` if the clip is a mask.
    :param transparent: `True` (default) if you want the alpha layer
         of the picture (if it exists) to be used as a mask.
    
    :ivar img: array representing the image of the clip.
        
    """

    def __init__(self, img, ismask=False, transparent=True, fromalpha=False):

        VideoClip.__init__(self, ismask=ismask)

        if isinstance(img, str):
            img = imread(img)
        
        if len(img.shape) == 3:
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

        self.img = img
        self.size = img.shape[:2][::-1]
        self.get_frame = lambda t: self.img


class ColorClip(VideoClip):

    """
    
    To be written
        
    """

    def __init__(self, size, col=(0, 0, 0), ismask=False):
        VideoClip.__init__(self, ismask=ismask)
        self.size = size
        w, h = size
        shape = (h, w) if isinstance(col, (int, float)) else (h, w, len(col))
        self.img = np.tile(col, w * h).reshape(shape)
        self.get_frame = lambda t: self.img


class TextClip(ImageClip):

    """ 
    
    A VideoClip originating from a script-generated text image.
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
       
    :param method: 'label' (autosized) or 'caption' (presized, wrapped)
    
    :param align: center | East | West | South | North
    
    :param transparent: ``True`` (default) if you want to take into account
        the transparency in the image.
    
    """

    def __init__(self, txt, size=None, color='black', bg_color='transparent',
                 fontsize=None, font='Times-New-Roman-Regular',
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

        if size != None:
            size = ('' if size[0] is None else str(size[0]),
                    '' if size[1] is None else str(size[1]))

        cmd = ("convert "
               + "-background transparent "
               + "-fill %s " % (color)
               + "-font %s " % font
               + ("" if (fontsize is None)
                  else "-pointsize %d " % fontsize)
               + ("" if (kerning is None)
                  else "-kerning %0.1f" % kerning)
               + ("" if (stroke_color is None)
                  else "-stroke %s -strokewidth %d " % (
                      stroke_color, stroke_width))
               + ("" if (size is None)
                  else "-size %sx%s " % (size[0], size[1]))
               + "-gravity %s " % align
               + ("" if (interline is None)
                  else "-interline-spacing %d " % interline)
               + "%s:'%s' " % (method, txt)
               + tempfile)

        if print_cmd:
            print cmd

        os.system(cmd)
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
        process = subprocess.Popen(['convert', '-list', 'font'],
                                   stdout=subprocess.PIPE)
        result = process.communicate()[0]
        lines = result.splitlines()

        if arg == 'font':
            return [l[8:] for l in lines if l.startswith("  Font:")]
        elif arg == 'color':
            return [l.split(" ")[1] for l in lines[2:]]


class CompositeVideoClip(VideoClip):

    """ 
    
    A VideoClip made of other videoclips displayed together.

    :param size: The size (height x width) of the final clip.

    :param clips: A list of videoclips. Each clip of the list will
       be displayed below the clips appearing after it in the list.
       For each clip:
       
       - The attribute ``pos`` determines where the clip is placed.
          See ``VideoClip.set_pos``
       - The mask of the clip determines which parts are visible.
        
       Finally, if all the clips in the list have their ``duration``
       attribute set, then the duration of the composite video clip
       is computed automatically

    :param transparent: if False, the clips are overlaid on a surface
      of the color `bg_color`. If True, the clips are overlaid on
      a transparent surface, so that all pixels that are transparent
      for all clips will be transparent in the composite clip. More
      precisely, the mask of the composite clip is then the composite
      of the masks of the different clips. Only use `transparent=True`
      when you intend to use your composite clip as part of another
      composite clip and you care about its transparency.
      
    """

    def __init__(self, size, clips, bg_color=None, transparent=False,
                 ismask=False):

        VideoClip.__init__(self)
        self.size = size
        self.ismask = ismask
        self.clips = clips
        self.transparent = transparent
        if bg_color is None:
            bg_color = 0.0 if self.ismask else (0, 0, 0)
        self.bg_color = bg_color
        self.bg = ColorClip(size, col=self.bg_color).get_frame(0)

        # compute duration
        ends = [c.end for c in self.clips]
        if not any([(e is None) for e in ends]):
            self.duration = max(ends)

        # compute audio
        audioclips = [v.audio for v in self.clips if v.audio != None]
        if len(audioclips) > 0:
            self.audio = CompositeAudioClip(audioclips)

        # compute mask
        if transparent:
            maskclips = [c.mask.set_pos(c.pos) for c in self.clips]
            self.mask = CompositeVideoClip(self.size, maskclips,
                                           transparent=False, ismask=True)

        def gf(t):
            """ The clips playing at time `t` are blitted over one
                another. """

            f = self.bg
            for c in self.playing_clips(t):
                    f = c.blit_on(f, t)
            return f

        self.get_frame = gf

    def playing_clips(self, t=0):
        """ Returns a list of the clips in the composite clips that are
            actually playing at the given time `t`. """
        return [c for c in self.clips if c.is_playing(t)]


def concat(cliplist, transition=None, bg_color=(0, 0, 0), transparent=False,
           ismask=False):
    """
    
    Makes one video clip by concatenating several clips of a list.
    (Concatenated means that they will be played one after another).
    if the clips do not have the same resolution, the final
    resolution will be such that no clip has to be resized. As
    a consequence the final clip has the height of the highest
    clip and the width of the widest clip of the list. All the
    clips with smaller dimensions will appear centered. The border
    will be transparent if mask=True, else it will be of the
    color specified by ``bg_color``. 
    
    :param cliplist: a list of video clips which must all have
                     their ``duration`` attributes set.
    :param transparent: if true, the resulting clip's mask will be the
              concatenation of the masks of the clips in the list. If
              the clips do not have the same resolution, the border around
              the smaller clips will be transparent. 
    :param transition: a clip that will be played between each two
                       clips of the list.     
                       
    """

    if transition:
        l = [[v, transition] for v in cliplist[:-1]]
        cliplist = reduce(lambda x, y: x + y, l) + [cliplist[-1]]

    sizes = [v.size for v in cliplist]
    tt = np.cumsum([0] + [c.duration for c in cliplist])

    if len(set(sizes)) == 1:  # All clips have the same size
        result = VideoClip()
        result.size = cliplist[0].size
        result.cliplist = cliplist
        result.tt = tt
        result.duration = tt[-1]

        def gf(t):
            i = max([i for i, e in enumerate(tt) if e <= t])
            return result.cliplist[i].get_frame(t - tt[i])
        result.get_frame = gf

    else:

        w = max([r[0] for r in sizes])
        h = max([r[1] for r in sizes])
        result = CompositeVideoClip((w, h),
                [c.set_start(t).set_pos(('center', 'center'))
                 for (c, t) in zip(cliplist, tt)],
                bg_color=bg_color,
                ismask=ismask, transparent=transparent)
    
    # Compute the mask if any
    
    if transparent and (not ismask):
        result.mask = concat([c.mask for c in cliplist], transparent=False,
                             ismask=True)
    
    
    # Compute the audio if any
    
    audios = [c.audio for c in cliplist if c.audio!=None]
    if len(audios)>1:
        result.audio = CompositeAudioClip([a.set_start(t)
                                         for a,t in zip(audios,tt)])
                                         
    return result
