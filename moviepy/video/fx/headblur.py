import numpy as np

#------- CHECKING DEPENDENCIES ----------------------------------------- 
try:
    import cv2
    headblur_possible = True
    if cv2.__version__ >= '3.0.0':
       cv2.CV_AA=cv2.LINE_AA
except:
    headblur_possible = False
#-----------------------------------------------------------------------


def headblur(clip,fx,fy,r_zone,r_blur=None):
    """
    Returns a filter that will blurr a moving part (a head ?) of
    the frames. The position of the blur at time t is
    defined by (fx(t), fy(t)), the radius of the blurring
    by ``r_zone`` and the intensity of the blurring by ``r_blur``.
    Requires OpenCV for the circling and the blurring.
    Automatically deals with the case where part of the image goes
    offscreen.
    """
    
    if r_blur is None: r_blur = 2*r_zone/3
    
    def fl(gf,t):
        
        im = gf(t)
        h,w,d = im.shape
        x,y = int(fx(t)),int(fy(t))
        x1,x2 = max(0,x-r_zone),min(x+r_zone,w)
        y1,y2 = max(0,y-r_zone),min(y+r_zone,h)
        region_size = y2-y1,x2-x1
        
        mask = np.zeros(region_size).astype('uint8')
        cv2.circle(mask, (r_zone,r_zone), r_zone, 255, -1,
                   lineType=cv2.CV_AA)
                               
        mask = np.dstack(3*[(1.0/255)*mask])
        
        orig = im[y1:y2, x1:x2]
        blurred = cv2.blur(orig,(r_blur, r_blur))
        im[y1:y2, x1:x2] = mask*blurred + (1-mask)*orig
        return im
    
    return clip.fl(fl)



#------- OVERWRITE IF REQUIREMENTS NOT MET -----------------------------
if not headblur_possible:
    doc = headblur.__doc__
    def headblur(clip,fx,fy,r_zone,r_blur=None):
        raise IOError("fx painting needs opencv")
    
    headblur.__doc__ = doc
#----------------------------------------------------------------------- 
