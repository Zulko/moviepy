import numpy as np

def blackwhite(clip, RGB = [1,1,1], preserve_luminosity=True):
	""" Desaturates the picture, makes it black and white.
	    method = sum (TODO: others) """
	if RGB == 'CRT_phosphor':
		RGB = [0.2125, 0.7154, 0.0721]
		
	return clip.fl_image(lambda im: np.dstack(3*[im.sum(axis=2)/3]) )
