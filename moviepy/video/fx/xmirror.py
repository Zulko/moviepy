def xmirror(clip, apply_to= "mask"):
	""" flips the clip horizontally (and its mask too, by default) """
	return clip.fl_image(gf(t)[:,::-1], apply_to = apply_to)
