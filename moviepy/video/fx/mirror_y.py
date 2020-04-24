def mirror_y(clip, apply_to="mask"):
    """ flips the clip vertically (and its mask too, by default) """
    return clip.with_image_filter(lambda f: f[::-1], apply_to=apply_to)
