def mirror_y(clip, apply_to="mask"):
    """ flips the clip vertically (and its mask too, by default) """
    return clip.fl_image(lambda f: f[::-1], apply_to=apply_to)
