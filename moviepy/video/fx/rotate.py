from moviepy.decorators import apply_to_mask
import numpy as np
try:
    from PIL import Image
    PIL_FOUND = True
    def pil_rotater(pic, angle, resample, expand):
        return np.array( Image.fromarray(pic).rotate(angle, expand=expand,
                                                     resample=resample))
except ImportError:
    PIL_FOUND = False

def rotate(clip, angle, unit='deg', resample="bicubic", expand=True):
    """
    Change unit to 'rad' to define angles as radians.
    If the angle is not one of 90, 180, -90, -180 (degrees) there will be
    black borders. You can make them transparent with

    >>> newclip = clip.add_mask().rotate(72)

    Parameters
    ===========

    clip
      A video clip

    angle
      Either a value or a function angle(t) representing the angle of rotation

    unit
      Unit of parameter `angle` (either `deg` for degrees or `rad` for radians)

    resample
      One of "nearest", "bilinear", or "bicubic".

    expand
      Only applIf False, the clip will maintain the same True, the clip will be resized so that the whole
    """
    
    resample = {"bilinear": Image.BILINEAR,
                "nearest": Image.NEAREST,
                "bicubic": Image.BICUBIC}[resample]

    if not hasattr(angle, '__call__'):
        # if angle is a constant, convert to a constant function
        a = +angle
        angle = lambda t: a

    transpo = [1,0] if clip.ismask else [1,0,2]

    def fl(gf, t):

        a = angle(t)
        im = gf(t)

        if unit == 'rad':
            a = 360.0*a/(2*np.pi)
        
        if (a==90) and expand:
            return np.transpose(im, axes=transpo)[::-1]
        elif (a==-90) and expand:
            return np.transpose(im, axes=transpo)[:,::-1]
        elif (a in [180, -180]) and expand:
            return im[::-1,::-1]
        elif not PIL_FOUND:
            raise ValueError('Without "Pillow" installed, only angles 90, -90,'
                             '180 are supported, please install "Pillow" with'
                             "pip install pillow")
        else:
            return pil_rotater(im, a, resample=resample, expand=expand)

    return clip.fl(fl, apply_to=["mask"])