


def rotation(clip, angle, apply_to_mask=True, unit='deg'):
    if unit == 'rad':
        angle = 360*angle/(2*3.14159)
    if angle ==90:
        return clip.fl_image(lambda im : im.T[::-1],
                              applyto='mask' if apply_to_mask else [])
    elif angle == -90:
        return clip.fl_image(lambda im : im.T,
                              applyto='mask' if apply_to_mask else [])
    elif angle == 180:
        return clip.fl_image(lambda im : im[::-1,::-1],
                              applyto='mask' if apply_to_mask else [])
    else:
        raise 'Angle not supported, only 90, -90, 180'
