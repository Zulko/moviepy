"""
This module implements all the functions to communicate with other Python
modules (PIL, matplotlib, mayavi, etc.)
"""

import numpy as np

def PIL_to_npimage(im):
    """ Transforms a PIL/Pillow image into a numpy RGB(A) image. """
    w,h = im.size
    d = (4 if im.mode=="RGBA" else 3)
    return +np.frombuffer(im.tobytes(), dtype='uint8').reshape((h,w,d))


def mplfig_to_npimage(fig):
    """ Updates the canvas and returns the RGB image (np array) """
    fig.canvas.draw() # update/draw the elements
    w,h = fig.canvas.get_width_height()
    buf = fig.canvas.tostring_rgb()
    image= +np.fromstring(buf,dtype=np.uint8)
    return image.reshape(h,w,3)