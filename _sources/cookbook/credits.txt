.. _autocredits:

==========================
Making Credits
==========================

Another advantage of scripting : we will see how to generate and animate some neat end credits. So here is a file ``EndCredits.txt``, which describes end credits in some weird yet understandable syntax (``.blank 4`` means "leave for blank lines"). ::

    .blank 4

    ..Executive Story Editor
    MARCEL DURAND

    ..Associate Producers
    MARTIN MARCEL
    DIDIER MARTIN

    ..Music Supervisor
    JEAN DIDIER

    ..First Assistant Director
    THOMAS JEAN

    ..Second Assistant Director
    MARIE THOMAS

    ..Guest Starring
    EDMOND MARIE
    MARIE JACQUES
    JACQUES MARIVON
    MARIVONNE ANDRE

    .blank 4

And here is a function that can parse this file to produce some neat credits: ::
    
    def make_credits(creditfile,width,stretch=30,color='white',
                     stroke_color='black', stroke_width=2,
                     font='Impact-Normal',fontsize=60):
        """ Makes a nice credits picture from a text file"""
        
        
        # PARSE THE TXT FILE
        
        with open(creditfile) as f:
            lines = f.readlines()
        
        lines = filter(lambda x:not x.startswith('\n'),lines) 
        texts = []
        oneline=True
        for l in  lines:
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
                   

        cc = CompositeVideoClip((left.w+right.w+stretch,right.h),
                        [left, right.set_pos((left.w+stretch,0))],
                        transparent=True)
        
        # SCALE TO THE REQUIRED SIZE
        
        scaled = cc.resize(width=width)
        
        # TRANSFORM THE WHOLE CREDIT CLIP INTO AN ImageCLip
        
        imclip = ImageClip(scaled.get_frame(0))
        amask = ImageClip(scaled.mask.get_frame(0),ismask=True)
        
        return imclip.set_mask(amask)
    
Applied on the previous text file, this function returns something like this:

.. figure:: credits.jpeg

Now, you can make this picture move with something like ::
    
    CompositeVideoClip(myVideo.res,
               [credits.set_pos(lambda t:('center',-speed*t))])
               
You can also do much more ! See for instance :ref:`mountainMask`.



