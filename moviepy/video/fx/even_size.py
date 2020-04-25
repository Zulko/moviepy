from moviepy.decorators import apply_to_mask


@apply_to_mask
def even_size(clip):
    """ 
    Crops the clip to make dimensions even.
    """
    w, h = clip.size
    w_even = w % 2 == 0
    h_even = h % 2 == 0
    if w_even and h_even:
        return clip

    if not w_even and not h_even:

        def image_filter(a):
            return a[:-1, :-1, :]

    elif w_even:

        def image_filter(a):
            return a[:, :-1, :]

    else:

        def image_filter(a):
            return a[:-1, :, :]

    return clip.with_image_filter(image_filter)
