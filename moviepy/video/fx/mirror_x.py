
def mirror_x(clip, applyto= "mask"):
	""" flips the clip horizontally (and its mask too, by default) """
	return clip.fl_image(lambda gf, t: gf(t)[:,::-1],
                          applyto = applyto)
