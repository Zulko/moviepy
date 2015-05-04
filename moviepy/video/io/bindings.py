"""
This module implements all the functions to communicate with other Python
modules (PIL, matplotlib, mayavi, etc.)
"""

import numpy as np

def PIL_to_npimage(im):
    """ Transforms a PIL/Pillow image into a numpy RGB(A) image.
        Actually all this do is returning numpy.array(im)."""
    return np.array(im)
    #w,h = im.size
    #d = (4 if im.mode=="RGBA" else 3)
    #return +np.frombuffer(im.tobytes(), dtype='uint8').reshape((h,w,d))


def mplfig_to_npimage(fig):
    """ Converts a matplotlib figure to a RGB frame after updating the canvas"""
    #  only the Agg backend now supports the tostring_rgb function
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    canvas = FigureCanvasAgg(fig)
    canvas.draw() # update/draw the elements

    # get the width and the height to resize the matrix
    l,b,w,h = canvas.figure.bbox.bounds
    w, h = int(w), int(h)

    #  exports the canvas to a string buffer and then to a numpy nd.array
    buf = canvas.tostring_rgb()
    image= np.fromstring(buf,dtype=np.uint8)
    return image.reshape(h,w,3)


