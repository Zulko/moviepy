
def scroll(clip, h=None, w=None, x_speed=0, y_speed=0, apply_to="mask"):
	""" Scrolls horizontally or vertically a clip, e.g. to make end
	    credits """
	if h is None: h = clip.h
	if w is None: w = clip.w
	def f(gf,t):
		x = int(x_speed*t)
		y = int(y_speed*t)
		return gf(t)[y:y+h, x:x+w]
	return clip.fl(fl, apply_to = apply_to)
