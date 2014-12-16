import numpy as np

def rotate(clip, angle, apply_to_mask=True, unit='deg'):
    
    if unit == 'rad':
        angle = 360*angle/(2*3.14159)
    
    transpo = [1,0] if clip.ismask else [1,0,2]
    angle_transfo = {
        90 : lambda im : np.transpose(im, axes=transpo)[::-1],
        -90: lambda im : np.transpose(im, axes=transpo)[:,::-1],
        180: lambda im : im[::-1,::-1]}
    
    if angle in angle_transfo:
        newclip =  clip.fl_image( angle_transfo[angle])
    else:
        raise ValueError('Angle not supported, only 90, -90, 180 at the moment')
    
    if apply_to_mask and (newclip.mask is not None):
        newclip.mask = newclip.mask.fx( rotation, angle,
                                        apply_to_mask=False,
                                        unit=unit)
    
    return newclip
