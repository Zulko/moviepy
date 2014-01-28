
def scroll(clip, h=None, w=None, x_speed=0, y_speed=0,
           x_start=0, y_start=0, applyto="mask"):
	""" Scrolls horizontally or vertically a clip, e.g. to make end
	    credits """
	if h is None: h = clip.h
	if w is None: w = clip.w
	def f(gf,t):
		x = x_start+int(x_speed*t)
		y = y_start+ int(y_speed*t)
		return gf(t)[y:y+h, x:x+w]
	return clip.fl(f, applyto = applyto)
