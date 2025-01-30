from dataclasses import dataclass

import numpy as np

from moviepy.Clip import Clip
from moviepy.Effect import Effect
from moviepy.video.VideoClip import ImageClip


@dataclass
class Margin(Effect):
    """Draws an external margin all around the frame.

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

    margin_size: int = None
    left: int = 0
    right: int = 0
    top: int = 0
    bottom: int = 0
    color: tuple = (0, 0, 0)
    opacity: float = 1.0

    def add_margin(self, clip: Clip):
        """Add margins to the clip."""
        if (self.opacity != 1.0) and (clip.mask is None) and not (clip.is_mask):
            clip = clip.with_mask()

        if self.margin_size is not None:
            self.left = self.right = self.top = self.bottom = self.margin_size

        def make_bg(w, h):
            new_w, new_h = w + self.left + self.right, h + self.top + self.bottom
            if clip.is_mask:
                shape = (new_h, new_w)
                bg = np.tile(self.opacity, (new_h, new_w)).astype(float).reshape(shape)
            else:
                shape = (new_h, new_w, 3)
                bg = np.tile(self.color, (new_h, new_w)).reshape(shape)
            return bg

        if isinstance(clip, ImageClip):
            im = make_bg(clip.w, clip.h)
            im[self.top : self.top + clip.h, self.left : self.left + clip.w] = clip.img
            return clip.image_transform(lambda pic: im)

        else:

            def filter(get_frame, t):
                pic = get_frame(t)
                h, w = pic.shape[:2]
                im = make_bg(w, h)
                im[self.top : self.top + h, self.left : self.left + w] = pic
                return im

            return clip.transform(filter)

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        # We apply once on clip and once on mask if we have one
        clip = self.add_margin(clip=clip)

        if clip.mask:
            clip.mask = self.add_margin(clip=clip.mask)

        return clip
