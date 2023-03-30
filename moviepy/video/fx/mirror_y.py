def mirror_y(clip, apply_to="mask"):
    """Flips the clip vertically (and its mask too, by default)."""
    return clip.image_transform(lambda img: img[::-1], apply_to=apply_to)
