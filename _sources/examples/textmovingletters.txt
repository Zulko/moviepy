=============================
Text with moving letters
=============================

I think this example illustrates well the interest of script-based editing (imagine doing that by hand).

.. raw:: html

        <center>
        <object><param name="movie"
        value="http://www.youtube.com/v/jj5qrHl5ZS0&hl=en_US&fs=1&rel=0">
        </param><param name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="http://www.youtube.com/v/jj5qrHl5ZS0&hl=en_US&fs=1&rel=0"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="550" height="450"></embed></object>
        </center>


Here is the code I used to generate the video above: we first define four ways of moving the letters, with four functions, then we make a clip for each of these movements, and concatenate everything. ::
    
    from moviepy import *
    import numpy as np
    
    # A nerdy tool for rotations.
    rotMatrix = lambda a: np.array( [[np.cos(a),np.sin(a)],
                                    [-np.sin(a),np.cos(a)]])
                                    
    
    # The letters appear from all directions
    def vortex(fpos,i,nletters):
        d = lambda t : 1.0/(0.3+t**8) #damping
        a = i*np.pi/ nletters # angle of the movement
        v = rotMatrix(a).dot([-1,0])
        if i%2 : v[1] = -v[1]
        return lambda t: fpos+400*d(t)*rotMatrix(0.5*d(t)*a).dot(v)
        
    
    # The letters appear from above
    def cascade(fpos,i,nletters):
        v = np.array([0,-1])
        d = lambda t : 1 if t<0 else abs(np.sinc(t)/(1+t**4))
        return lambda t: fpos+v*400*d(t-0.15*i)
    
    
    # The letters arrive from the right
    def arrive(fpos,i,nletters):
        v = np.array([-1,0])
        d = lambda t : max(0, 3-3*t)
        return lambda t: fpos-400*v*d(t-0.2*i)
        
    
    # The letters 'explode'    
    def vortexout(fpos,i,nletters):
        d = lambda t : max(0,t) #damping
        a = i*np.pi/ nletters # angle of the movement
        v = rotMatrix(a).dot([-1,0])
        if i%2 : v[1] = -v[1]
        return lambda t: fpos+400*d(t-0.1*i)*rotMatrix(-0.2*d(t)*a).dot(v)
    
    
    screensize = (720,460)
    txtClip = TextClip('Cool effect',color='white', font="Amiri-Bold",
                       kerning = 5, fontsize=100)

    clips = [ CompositeVideoClip(screensize,
              moveLetters(txtClip,screensize,funcpos)).
              subclip(0,5)
              for funcpos in [vortex, cascade, arrive, vortexout] ]

    concat(clips).to_movie('coolTextEffects.avi')




Ok, maybe you saw it, the central function in the script above is a function called ``moveLetters``. This is the function that recognizes the letters in the text clip and make them move, which is far from trivial. So here is the code for ``moveLetters``: ::
    
    from skimage.morphology import label
    import scipy.ndimage as ndi

    def moveLetters(txtClip,screensize, funcpos,rem_thr=500):
        """ 
        Takes the textclip,centers it, separates the letters,
        sets the position of each letter according to funcpos
        
        funcpos : funcpos(fpos,i,nletters) where
           - fpos : final position of the letter
           - i : index of the letter
           - nletters : total number of letters
           Returns: a position function t-> (x(t),y(t))
            
        rem_thr : all 'letters' with size < rem_Thr will be
             considered false positives and will be removed
              
         
        >>> letters = vortexLetters(txtClip,screensize,funcpos)
        >>> CompositeVideoClip(screensize,letters,transparent=True)
           
        """
        
        # First place the text at the center of the clip
        # This will only be useful to get the position of
        # the letters in the clip
        cvc = CompositeVideoClip(screensize,
                [txtClip.set_pos(['center','center'])],
                 transparent=True)
        image = cvc.get_frame(0)
        mask = cvc.mask.get_frame(0)
        
        # segment/label the image with scikit-image's function
        mat = label(image[:,:,0])
        #find the positions of the objects in the image
        slices = ndi.find_objects(mat)
        #cool trick to remove letter holes (in 'o','e','a', etc.)
        slices = [e for e in slices if  mask[e[0],e[1]].mean() >0.2]
        # remove very small slices
        slices = [e for e in slices if  image[e[0],e[1]].size > rem_thr]
        # Sort the slices from left to right
        slices = sorted(slices, key = lambda s : s[1].start)
        
        
        letters = []
        for i,(sy,sx) in enumerate(slices):
            """ crop each letter separately and set position """
            sy = slice(sy.start-1,sy.stop+1)
            sx = slice(sx.start-1,sx.stop+1)
            letter = ImageClip(image[sy,sx])
            letter.mask = ImageClip(mask[sy,sx],ismask=True)
            finalpos = np.array((sx.start,sy.start)) # final position
            letter.pos = funcpos(finalpos,i,len(slices))
            letters.append(letter)
       
        return letters
        
