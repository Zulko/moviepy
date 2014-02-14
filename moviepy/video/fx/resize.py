resize_possible = True

try:
    
    import cv2
    resizer = lambda pic, newsize : cv2.resize(pic.astype('uint8'),
                tuple(map(int, newsize)),
                interpolation=cv2.INTER_AREA)
                
except ImportError:
    
    try:
        
        from PIL import Image
        import numpy as np
        def resizer(pic, newsize):
            newsize = map(int, newsize)[::-1]
            shape = pic.shape
            if len(shape)==3:
                newshape = (newsize[0],newsize[1], shape[2] )
            else:
                newshape = (newsize[0],newsize[1])
                
            pilim = Image.fromarray(pic)
            resized_pil = pilim.resize(newsize[::-1], Image.ANTIALIAS)
            arr = np.fromstring(resized_pil.tostring(), dtype='uint8')
            return arr.reshape(newshape)
            
    except ImportError:
        
        try:
            
            import scipy.misc.imresize as imresize
            resizer = lambda pic, newsize : imresize(pic,
                                               map(int, newsize[::-1]))
                                               
        except ImportError:
            
            resize_possible = False
        
    
from moviepy.decorators import apply_to_mask
    
@apply_to_mask
def resize(clip, newsize=None, height=None, width=None):
    """ 
    Returns a video clip that is a resized version of the clip.
    
    :param newsize: can be either ``(height,width)`` in pixels or
        a float representing a scaling factor. Or a function of time
        returning one of these.
            
    :param width: width of the new clip in pixel. The height is
        then computed so that the width/height ratio is conserved. 
            
    :param height: height of the new clip in pixel. The width is
        then computed so that the width/height ratio is conserved.
             
    >>> myClip.resize( (460,720) ) # New resolution: (460,720)
    >>> myClip.resize(0.6) # width and heigth multiplied by 0.6
    >>> myClip.resize(width=800) # height computed automatically.
    >>> myClip.resize(lambda t : 1+0.02*t) # slow swelling of the clip
    
    """
    w, h = clip.size
    
    if newsize != None:
        def trans_newsize(ns):
            if isinstance(ns, (int, float)):
                return [ns * w, ns * h]
            else:
                return ns
        if hasattr(newsize, "__call__"):
            newsize2 = lambda t : trans_newsize(newsize(t))
            if clip.ismask:
                fl = lambda gf,t: 1.0*resizer((255 * gf(t)).astype('uint8'),
                    newsize2(t))/255
            else:
                fl = lambda gf,t: resizer(gf(t).astype('uint8'),newsize2(t))
                
            return clip.fl(fl)
            
        else:
            newsize = trans_newsize(newsize)
        

    elif height != None:
        newsize = [w * height / h, height]
    elif width != None:
        newsize = [width, h * width / w]

    if clip.ismask:
        fl = lambda pic: 1.0*resizer((255 * pic).astype('uint8'),
            newsize)/255
    else:
        fl = lambda pic: resizer(pic.astype('uint8'), newsize)

    return clip.fl_image(fl)


if not resize_possible:
    doc = resize.__doc__
    def resize(clip, newsize=None, height=None, width=None):
        raise ImportError("fx resize needs OpenCV or Scipy or PIL")
    resize.__doc__ = doc
