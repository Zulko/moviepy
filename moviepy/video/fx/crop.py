def crop(clip, x1=None, y1=None, x2=None, y2=None, width=None, height=None, x_center=None, y_center=None):
    """
    Returns a new clip in which just a rectangular subregion of the
    original clip is conserved. x1,y1 indicates the top left corner and
    x2,y2 is the lower right corner of the croped region.
    All coordinates are in pixels. Float numbers are accepted.
    
    To crop an arbitrary rectangle:
    
    >>> crop(clip, x1=50, y1=60, x2=460, y2=275)
    
    Only remove the part above y=30:
    
    >>> crop(clip, y1=30)
    
    Crop a rectangle that starts 10 pixels left and is 200px wide
    
    >>> crop(clip, x1=10, width=200)
    
    Crop a rectangle centered in x,y=(300,400), width=50, height=150 :
    
    >>> crop(clip,  x_center=300 , y_center=400,
                        width=50, height=150)
    
    Any combination of the above should work, like for this rectangle
    centered in x=300, with explicit y-boundaries:
    
    >>> crop(x_center=300, width=400, y1=100, y2=600)
    
    """

    if width and x1 is not None:
        x2 = x1 + width
    elif width and x2 is not None:
        x1 = x2 - width

    if height and y1 is not None:
        y2 = y1 + height
    elif height and y2 is not None:
        y1 = y2 - height

    if x_center:
        x1, x2 = x_center - width / 2, x_center + width / 2

    if y_center:
        y1, y2 = y_center - height / 2, y_center + height / 2

    x1 = x1 or 0
    y1 = y1 or 0
    x2 = x2 or clip.size[0]
    y2 = y2 or clip.size[1]

    return clip.fl_image(lambda pic: pic[int(y1) : int(y2), int(x1) : int(x2)], apply_to=["mask"])
