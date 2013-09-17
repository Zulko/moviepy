"""
Classes for advantageous handling of static clips.
ImageClip, ColorClip, TextClip
"""

import subprocess
import os
import numpy as np
import moviepy.video.VideoClip as VC
import moviepy.video.io.readers as readers



class ImageClip(VC.VideoClip):

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

        VC.VideoClip.__init__(self, ismask=ismask)

        if isinstance(img, str):
            img = readers.read_image(img,with_mask=transparent)
        
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
        newclip = VC.VideoClip.fl(self,fl, applyto=applyto,
                               keep_duration=keep_duration)
        newclip.__class__ = VC.VideoClip
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
    
    def fl_time(self, applyto =['mask', 'audio']):
        """
        This method does nothing for ImageClips (but it may affect their
        masks of their audios). The result is still an ImageClip
        """
        newclip = copy(self, keep_class=True)
        
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
        "-type",  "truecolormatte", tempfile]
        
        if print_cmd:
            print " ".join(cmd)

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
