def crop(clip, x1=None, y1=None, x2=None, y2=None,
         width = None, height=None,
         x_center= None, y_center=None):
    """
    >>> crop(clip, x1,y1,x2,y2) # defines the rectangle of the crop
    >>> crop(clip, x1=10, width=200)
    
    
    """
    
    
    if width:
        if x1 is not None:
            x2 = x1+width
        else:
            x1 = x2-width
    
    if height:
        if y1 is not None:
            y2 = y1+height
        else:
            y1 = y2 - height
    
    if x_center:
        x1, x2 = x_center - width/2, x_center + width/2
    
    if y_center:
        y1, y2 = y_center - height/2, y_center + height/2
    
    if x1 is None:
        x1 = 0
    if y1 is None:
        y1 = 0
    if x2 is None:
        x2 = clip.size[0]
    if y2 is None:
        y2 = clip.size[1]
    
    return clip.fl_image(lambda pic: pic[y1:y2, x1:x2],
                         applyto=['mask'])
