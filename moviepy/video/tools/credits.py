"""
This module contains different fonctions to make end and opening
credits, even though it is difficult to fill everyone needs in this
matter.
"""

from moviepy.video.VideoClip import TextClip, ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx import resize

def credits1(creditfile,width,stretch=30,color='white',
                 stroke_color='black', stroke_width=2,
                 font='Impact-Normal',fontsize=60):
    """
    
    The first credits I imagined. They take as argument a file like: ::
        
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
        
    And produce an ImageClip that looks like :
    
        Executive Story Editor    MARCEL DURAND
           Associate Producers    MARTIN MARCEL
                                  DIDIER MARTIN
              Music Supervisor    JEAN DIDIER
    
    :param width: total width of the credits text
    :param stretch: stretch in pixels between the jobs and the names.
    
    The other keywords are passed to the ``TextClip``s
    """
    
    
    # PARSE THE TXT FILE
    
    with open(creditfile) as f:
        lines = f.readlines()
    
    lines = filter(lambda x:not x.startswith('\n'),lines) 
    texts = []
    oneline=True
    for l in  lines:
        if not l.startswith('#'):
            if l.startswith('.blank'):
                for i in range(int(l.split(' ')[1])):
                    texts.append(['\n','\n'])
            elif  l.startswith('..'):
                texts.append([l[2:],''])
                oneline=True
            else:
                if oneline:
                    texts.append(['',l])
                    oneline=False
                else:
                    texts.append(['\n',l])
               
    left,right = [ "".join(l) for l in zip(*texts)]
    
    # MAKE TWO COLUMNS FOR THE CREDITS
    
    left,right =  [TextClip(txt,color=color,stroke_color=stroke_color,
                                stroke_width=stroke_width,font=font,
                                fontsize=fontsize,align=al)
               for txt,al in [(left,'East'),(right,'West')]]
               

    cc = CompositeVideoClip( [left, right.set_pos((left.w+stretch,0))],
                             size = (left.w+right.w+stretch,right.h),
                             transparent=True)
    
    # SCALE TO THE REQUIRED SIZE
    
    scaled = cc.fx(resize , width=width)
    
    # TRANSFORM THE WHOLE CREDIT CLIP INTO AN ImageCLip
    
    imclip = ImageClip(scaled.get_frame(0))
    amask = ImageClip(scaled.mask.get_frame(0),ismask=True)
    
    return imclip.set_mask(amask)
