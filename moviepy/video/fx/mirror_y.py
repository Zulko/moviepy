def mirror_y(clip, apply_to= "mask"):
	""" flips the clip vertically (and its mask too, by default) """
	return clip.fl_image(lambda gf, t : gf(t)[::-1],
                          applyto = applyto)
