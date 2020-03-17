"""
This module contains different functions to make end and opening
credits, even though it is difficult to fill everyone needs in this
matter.
"""

from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.resize import resize
from moviepy.video.VideoClip import ImageClip, TextClip


def credits1(creditfile, width, stretch=30, color='white', stroke_color='black',
             stroke_width=2, font='Impact-Normal', fontsize=60, gap=0):
    """

    Parameters
    -----------
    
    creditfile
      A text file whose content must be as follows: ::
        
        # This is a comment
        # The next line says : leave 4 blank lines
        .blank 4
        
        ..Executive Story Editor
        MARCEL DURAND
        
        ..Associate Producers
        MARTIN MARCEL
        DIDIER MARTIN
        
        ..Music Supervisor
        JEAN DIDIER
    
    width
      Total width of the credits text in pixels
      
    gap
      Horizontal gap in pixels between the jobs and the names
    
    color
      Color of the text. See ``TextClip.list('color')``
      for a list of acceptable names.

    font
      Name of the font to use. See ``TextClip.list('font')`` for
      the list of fonts you can use on your computer.

    fontsize
      Size of font to use

    stroke_color
      Color of the stroke (=contour line) of the text. If ``None``,
      there will be no stroke.

    stroke_width
      Width of the stroke, in pixels. Can be a float, like 1.5.
    
        
    Returns
    ---------
    
    image
      An ImageClip instance that looks like this and can be scrolled
      to make some credits:

          Executive Story Editor    MARCEL DURAND
             Associate Producers    MARTIN MARCEL
                                    DIDIER MARTIN
                Music Supervisor    JEAN DIDIER
              
    """

    # PARSE THE TXT FILE
    texts = []
    oneline = True
    
    with open(creditfile) as f:
        for l in f:
            if l.startswith(('\n', '#')):
                # exclude blank lines or comments
                continue
            elif l.startswith('.blank'):
                # ..blank n  
                for i in range(int(l.split(' ')[1])):
                    texts.append(['\n', '\n'])
            elif l.startswith('..'):
                texts.append([l[2:], ''])
                oneline = True
            elif oneline:
                texts.append(['', l])
                oneline = False
            else:
                texts.append(['\n', l])
       
    left, right = ("".join(l) for l in zip(*texts))
    
    # MAKE TWO COLUMNS FOR THE CREDITS    
    left, right = [TextClip(txt, color=color, stroke_color=stroke_color,
                            stroke_width=stroke_width, font=font,
                            fontsize=fontsize, align=al)
                   for txt, al in [(left, 'East'), (right, 'West')]]

    cc = CompositeVideoClip([left, right.set_position((left.w + gap, 0))],
                            size=(left.w + right.w + gap, right.h),
                            bg_color=None)
    
    # SCALE TO THE REQUIRED SIZE
    
    scaled = resize(cc, width=width)
    
    # TRANSFORM THE WHOLE CREDIT CLIP INTO AN ImageCLip
    
    imclip = ImageClip(scaled.get_frame(0))
    amask = ImageClip(scaled.mask.get_frame(0), ismask=True)
    
    return imclip.set_mask(amask)
