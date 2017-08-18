resize_possible = True

try:
    # TRY USING OpenCV AS RESIZER
    #raise ImportError #debugging
    import cv2
    import numpy as np
    def resizer (pic, newsize):
        lx, ly = int(newsize[0]), int(newsize[1])
        if lx > pic.shape[1] or ly > pic.shape[0]:
            # For upsizing use linear for good quality & decent speed
            interpolation = cv2.INTER_LINEAR
        else:
            # For dowsizing use area to prevent aliasing
            interpolation = cv2.INTER_AREA
        return cv2.resize(+pic.astype('uint8'), (lx, ly),
                          interpolation=interpolation)

    resizer.origin = "cv2"
                
except ImportError:
    
    
    try:
        # TRY USING PIL/PILLOW AS RESIZER
        from PIL import Image
        import numpy as np
        def resizer(pic, newsize):
            newsize = list(map(int, newsize))[::-1]
            shape = pic.shape
            if len(shape)==3:
                newshape = (newsize[0],newsize[1], shape[2] )
            else:
                newshape = (newsize[0],newsize[1])
                
            pilim = Image.fromarray(pic)
            resized_pil = pilim.resize(newsize[::-1], Image.BICUBIC)
            #arr = np.fromstring(resized_pil.tostring(), dtype='uint8')
            #arr.reshape(newshape)
            return np.array(resized_pil)
            
        resizer.origin = "PIL"
            
    except ImportError:
        # TRY USING SCIPY AS RESIZER
        try:
            from scipy.misc import imresize
            resizer = lambda pic, newsize : imresize(pic,
                                            map(int, newsize[::-1]))
            resizer.origin = "Scipy"
                                               
        except ImportError:
            resize_possible = False
            
        
        
    
from moviepy.decorators import apply_to_mask
   

def resize(clip, newsize=None, height=None, width=None, apply_to_mask=True,
           strict_even=False, threshold=2.0, precision=0.00005, **kwargs):
    """ 
    Returns a video clip that is a resized version of the clip.
    
    Parameters
    ------------
    
    newsize:
      Can be either 
        - ``(height,width)`` in pixels or a float representing
        - A scaling factor, like 0.5
        - A function of time returning one of these.
            
    width:
      width of the new clip in pixel. The height is then computed so
      that the width/height ratio is conserved. 
            
    height:
      height of the new clip in pixel. The width is then computed so
      that the width/height ratio is conserved.
    
    Examples
    ----------
             
    >>> myClip.resize( (460,720) ) # New resolution: (460,720)
    >>> myClip.resize(0.6) # width and heigth multiplied by 0.6
    >>> myClip.resize(width=800) # height computed automatically.
    >>> myClip.resize(lambda t : 1+0.02*t) # slow swelling of the clip
    
    """

    w, h = clip.size
    ratio = float(w) / h
    
    if newsize is not None:
        
        def trans_newsize(scale, threshold, precision):
            
            if isinstance(scale, (int, float)):
                if strict_even:
                    return calibrate(scale, threshold, precision)
                else:
                    return [scale * w, scale * h]
            else:
                return scale

        def calibrate(scale, threshold, precision):
            new_w = round(scale * w / 2.0) * 2
            new_h = round(scale * h / 2.0) * 2
            new_ratio = new_w / new_h
            max_iter = int(0.1 / precision)

            distort = abs(new_ratio - ratio) * 1000 / ratio
            bias = precision
            scale_new = scale

            min_distort = distort
            best_scale = scale
            for i in range(max_iter):
                if min_distort < threshold:
                    break

                scale_new = scale + bias
                new_ratio = round(scale_new * w / 2.0) / round(scale_new * h / 2.0)
                distort = abs(new_ratio - ratio) * 1000 / ratio

                if distort < min_distort:
                    min_distort = distort
                    best_scale = scale_new

                if bias > 0:
                    bias *= -1
                else:
                    bias = precision - bias

            if min_distort >= threshold:
                print "Failed to preserve ratio, disrtort %.3f." % min_distort

            new_w = round(best_scale * w / 2.0) * 2
            new_h = round(best_scale * h / 2.0) * 2

            return [new_w, new_h]

        if hasattr(newsize, "__call__"):
            
            newsize2 = lambda t : trans_newsize(newsize(t), threshold, precision)
            
            if clip.ismask:
                
                fun = lambda gf,t: (1.0*resizer((255 * gf(t)).astype('uint8'),
                                                 newsize2(t))/255)
            else:
                
                fun = lambda gf,t: resizer(gf(t).astype('uint8'),
                                          newsize2(t))
                
            if apply_to_mask and clip.mask is not None:
                clip.mask = resize(clip.mask, newsize2, apply_to_mask=False)

            return clip.fl(fun, keep_duration=True)
            
        else:
            
            newsize = trans_newsize(newsize, threshold, precision)
        

    elif height is not None:
        
        if hasattr(height, "__call__"):
            fun = lambda t : 1.0*int(height(t))/h
            return resize(clip, fun)


        else:

            newsize = [w * height / h, height]
        
    elif width is not None:

        if hasattr(width, "__call__"):
            fun = lambda t : 1.0*width(t)/w
            return resize(clip, fun)
        
        newsize = [width, h * width / w]
        
        
    # From here, the resizing is constant (not a function of time), size=newsize

    if clip.ismask:
        fl = lambda pic: (1.0*resizer((255 * pic).astype('uint8'), newsize)/255.0).astype(np.float32)
            
    else:
        fl = lambda pic: resizer(pic.astype('uint8'), newsize)

    newclip = clip.fl_image(fl)

    if apply_to_mask and clip.mask is not None:
        newclip.mask = resize(clip.mask, newsize, apply_to_mask=False)

    return newclip


if not resize_possible:
    
    doc = resize.__doc__
    def resize(clip, newsize=None, height=None, width=None):
        raise ImportError("fx resize needs OpenCV or Scipy or PIL")
    resize.__doc__ = doc
