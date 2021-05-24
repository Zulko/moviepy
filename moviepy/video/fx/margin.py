import numpy as np

from moviepy.decorators import apply_to_mask
from moviepy.video.VideoClip import ImageClip


@apply_to_mask
def margin(
    clip,
    margin_size=None,
    left=0,
    right=0,
    top=0,
    bottom=0,
    color=(0, 0, 0),
    opacity=1.0,
):
    """
    Draws an external margin all around the frame.

    Parameters
    ----------

    margin_size : int, optional
      If not ``None``, then the new clip has a margin size of
      size ``margin_size`` in pixels on the left, right, top, and bottom.

    left : int, optional
      If ``margin_size=None``, margin size for the new clip in left direction.

    right : int, optional
      If ``margin_size=None``, margin size for the new clip in right direction.

    top : int, optional
      If ``margin_size=None``, margin size for the new clip in top direction.

    bottom : int, optional
      If ``margin_size=None``, margin size for the new clip in bottom direction.

    color : tuple, optional
      Color of the margin.

    opacity : float, optional
      Opacity of the margin. Setting this value to 0 yields transparent margins.
    """
    if (opacity != 1.0) and (clip.mask is None) and not (clip.is_mask):
        clip = clip.add_mask()

    if margin_size is not None:
        left = right = top = bottom = margin_size

    def make_bg(w, h):
        new_w, new_h = w + left + right, h + top + bottom
        if clip.is_mask:
            shape = (new_h, new_w)
            bg = np.tile(opacity, (new_h, new_w)).astype(float).reshape(shape)
        else:
            shape = (new_h, new_w, 3)
            bg = np.tile(color, (new_h, new_w)).reshape(shape)
        return bg

    if isinstance(clip, ImageClip):
        im = make_bg(clip.w, clip.h)
        im[top : top + clip.h, left : left + clip.w] = clip.img
        return clip.image_transform(lambda pic: im)

    else:

        def filter(get_frame, t):
            pic = get_frame(t)
            h, w = pic.shape[:2]
            im = make_bg(w, h)
            im[top : top + h, left : left + w] = pic
            return im

        return clip.transform(filter)
