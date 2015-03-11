"""
This module deals with making images (np arrays). It provides drawing
methods that are difficult to do with the existing Python libraries.
"""

import numpy as np

def blit(im1, im2, pos=[0, 0], mask=None, ismask=False):
    """ Blit an image over another.
    
    Blits ``im1`` on ``im2`` as position ``pos=(x,y)``, using the
    ``mask`` if provided. If ``im1`` and ``im2`` are mask pictures
    (2D float arrays) then ``ismask`` must be ``True``.
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

    if mask is not None:
        mask = mask[y1:y2, x1:x2]
        if len(im1.shape) == 3:
            mask = np.dstack(3 * [mask])
        blit_region = new_im2[yp1:yp2, xp1:xp2]
        new_im2[yp1:yp2, xp1:xp2] = (
            1.0 * mask * blitted + (1.0 - mask) * blit_region)
    else:
        new_im2[yp1:yp2, xp1:xp2] = blitted

    return new_im2.astype('uint8') if (not ismask) else new_im2



def color_gradient(size,p1,p2=None,vector=None, r=None, col1=0,col2=1.0,
              shape='linear', offset = 0):
    """Draw a linear, bilinear, or radial gradient.
    
    The result is a picture of size ``size``, whose color varies
    gradually from color `col1` in position ``p1`` to color ``col2``
    in position ``p2``.
    
    If it is a RGB picture the result must be transformed into
    a 'uint8' array to be displayed normally:
     
     
    Parameters
    ------------      
    
    size
      Size (width, height) in pixels of the final picture/array.
    
    p1, p2
      Coordinates (x,y) in pixels of the limit point for ``col1``
      and ``col2``. The color 'before' ``p1`` is ``col1`` and it
      gradually changes in the direction of ``p2`` until it is ``col2``
      when it reaches ``p2``.
    
    vector
      A vector [x,y] in pixels that can be provided instead of ``p2``.
      ``p2`` is then defined as (p1 + vector).
    
    col1, col2
      Either floats between 0 and 1 (for gradients used in masks)
      or [R,G,B] arrays (for colored gradients).
               
    shape
      'linear', 'bilinear', or 'circular'.
      In a linear gradient the color varies in one direction,
      from point ``p1`` to point ``p2``.
      In a bilinear gradient it also varies symetrically form ``p1``
      in the other direction.
      In a circular gradient it goes from ``col1`` to ``col2`` in all
      directions.
    
    offset
      Real number between 0 and 1 indicating the fraction of the vector
      at which the gradient actually starts. For instance if ``offset``
      is 0.9 in a gradient going from p1 to p2, then the gradient will
      only occur near p2 (before that everything is of color ``col1``)
      If the offset is 0.9 in a radial gradient, the gradient will
      occur in the region located between 90% and 100% of the radius,
      this creates a blurry disc of radius d(p1,p2).  
    
    Returns
    --------
    
    image
      An Numpy array of dimensions (W,H,ncolors) of type float
      representing the image of the gradient.
      
    
    Examples
    ---------
    
    >>> grad = color_gradient(blabla).astype('uint8')
    
    """
    
    # np-arrayize and change x,y coordinates to y,x
    w,h = size
    
    col1, col2 = map(lambda x : np.array(x).astype(float), [col1, col2])
    
    if shape == 'bilinear':
        if vector is None:
            vector = np.array(p2) - np.array(p1)
        m1,m2 = [ color_gradient(size, p1, vector=v, col1 = 1.0, col2 = 0,
                           shape = 'linear', offset= offset)
                  for v in [vector,-vector]]
                  
        arr = np.maximum(m1,m2)
        if col1.size > 1:
            arr = np.dstack(3*[arr])
        return arr*col1 + (1-arr)*col2
        
    
    p1 = np.array(p1[::-1]).astype(float)
    
    if vector is None:
        if p2 is not None:
            p2 = np.array(p2[::-1])
            vector = p2-p1
    else:
        vector = np.array(vector[::-1])
        p2 = p1 + vector
    
    if vector is not None:    
        norm = np.linalg.norm(vector)
    
    M = np.dstack(np.meshgrid(range(w),range(h))[::-1]).astype(float)
    
    if shape == 'linear':
        
        n_vec = vector/norm**2 # norm 1/norm(vector)
        
        p1 = p1 + offset*vector
        arr = (M- p1).dot(n_vec)/(1-offset)
        arr = np.minimum(1,np.maximum(0,arr))
        if col1.size > 1:
            arr = np.dstack(3*[arr])
        return arr*col1 + (1-arr)*col2
    
    elif shape == 'radial':
        if r is None:
            r = norm
        if r==0:
            arr = np.ones((h,w))
        else:
            arr = (np.sqrt(((M- p1)**2).sum(axis=2)))-offset*r
            arr = arr / ((1-offset)*r)
            arr = np.minimum(1.0,np.maximum(0, arr) )
            
        if col1.size > 1:
            arr = np.dstack(3*[arr])
        return (1-arr)*col1 + arr*col2
        

def color_split(size,x=None,y=None,p1=None,p2=None,vector=None,
               col1=0,col2=1.0, grad_width=0):
    """Make an image splitted in 2 colored regions.
    
    Returns an array of size ``size`` divided in two regions called 1 and
    2 in wht follows, and which will have colors col& and col2
    respectively.
    
    Parameters
    -----------
    
    x: (int)
      If provided, the image is splitted horizontally in x, the left
      region being region 1.
        
    y: (int)
      If provided, the image is splitted vertically in y, the top region
      being region 1.
    
    p1,p2:
      Positions (x1,y1),(x2,y2) in pixels, where the numbers can be
      floats. Region 1 is defined as the whole region on the left when
      going from ``p1`` to ``p2``.
    
    p1, vector:
      ``p1`` is (x1,y1) and vector (v1,v2), where the numbers can be
      floats. Region 1 is then the region on the left when starting
      in position ``p1`` and going in the direction given by ``vector``.
       
    gradient_width
      If not zero, the split is not sharp, but gradual over a region of
      width ``gradient_width`` (in pixels). This is preferable in many
      situations (for instance for antialiasing). 
     
    
    Examples
    ---------
    
    >>> size = [200,200]
    >>> # an image with all pixels with x<50 =0, the others =1
    >>> color_split(size, x=50, col1=0, col2=1)
    >>> # an image with all pixels with y<50 red, the others green
    >>> color_split(size, x=50, col1=[255,0,0], col2=[0,255,0])
    >>> # An image splitted along an arbitrary line (see below) 
    >>> color_split(size, p1=[20,50], p2=[25,70] col1=0, col2=1)
        
    """
    
    if grad_width or ( (x is None) and (y is None)):
        if p2 is not None:
            vector = (np.array(p2) - np.array(p1))
        elif x is not None:
            vector = np.array([0,-1.0])
            p1 = np.array([x, 0])
        elif y is not None:
            vector = np.array([1.0, 0.0])
            p1 = np.array([0,y])

        x,y = vector
        vector = np.array([y,-x]).astype('float')
        norm = np.linalg.norm(vector)
        vector =  max(0.1,grad_width)*vector/norm
        return color_gradient(size,p1,vector=vector,
                         col1 = col1, col2 = col2, shape='linear')
    else:
        
        w,h = size
        shape = (h, w) if np.isscalar(col1) else (h, w, len(col1))
        arr = np.zeros(shape)
        if x:
            arr[:,:x] = col1
            arr[:,x:] = col2
        elif y:
            arr[:y] = col1
            arr[y:] = col2
            
        return arr
     
    # if we are here, it means we didn't exit with a proper 'return'
    print( "Arguments in color_split not understood !" )
    raise
    
def circle(screensize, center, radius, col1=1.0, col2=0, blur=1):
    """ Draw an image with a circle.
    
    Draws a circle of color ``col1``, on a background of color ``col2``,
    on a screen of size ``screensize`` at the position ``center=(x,y)``,
    with a radius ``radius`` but slightly blurred on the border by ``blur``
    pixels
    """
    return color_gradient(screensize,p1=center,r=radius, col1=col1,
              col2=col2, shape='radial', offset = 0 if (radius==0) else
                                              1.0*(radius-blur)/radius)
