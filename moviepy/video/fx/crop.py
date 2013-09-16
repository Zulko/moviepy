def crop(clip, x1=0, y1=0, x2=None, y2=None):
	if x2 is None:
		x2 = clip.size[0]
	if y2 is None:
		y2 = clip.size[1]
	return clip.fl_image(lambda pic: pic[y1:y2, x1:x2],
						 applyto=['mask'])
