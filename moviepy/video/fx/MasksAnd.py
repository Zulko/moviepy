from dataclasses import dataclass
from typing import Union

import numpy as np

from moviepy.Clip import Clip
from moviepy.Effect import Effect
from moviepy.video.VideoClip import ImageClip
from moviepy.video.tools import cupy_utils


@dataclass
class MasksAnd(Effect):
    """Returns the logical 'and' (minimum pixel color values) between two masks.

    The result has the duration of the clip to which has been applied, if it has any.

    Parameters
    ----------

    other_clip ImageClip or np.ndarray
      Clip used to mask the original clip.

    Examples
    --------

    .. code:: python

        clip = ColorClip(color=(255, 0, 0), size=(1, 1))      # red
        mask = ColorClip(color=(0, 255, 0), size=(1, 1))      # green
        masked_clip = clip.with_effects([vfx.MasksAnd(mask)]) # black
        masked_clip.get_frame(0)
        [[[0 0 0]]]
    """

    other_clip: Union[Clip, np.ndarray]

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        # to ensure that 'and' of two ImageClips will be an ImageClip
        if isinstance(self.other_clip, ImageClip):
            self.other_clip = self.other_clip.img

        other_np = self.other_clip if isinstance(self.other_clip, np.ndarray) else None
        other_cp = None

        def _min(frame, other):
            if cupy_utils.is_cuda_array(frame) or cupy_utils.is_cuda_array(other):
                cp = cupy_utils.cupy()
                a = frame if cupy_utils.is_cuda_array(frame) else cp.asarray(frame)
                b = other if cupy_utils.is_cuda_array(other) else cp.asarray(other)
                return cp.minimum(a, b)
            return np.minimum(frame, other)

        if isinstance(self.other_clip, np.ndarray):
            def flim(frame):
                nonlocal other_cp
                if cupy_utils.is_cuda_array(frame):
                    if other_cp is None:
                        other_cp = cupy_utils.cupy().asarray(other_np)
                    return _min(frame, other_cp)
                return _min(frame, other_np)

            return clip.image_transform(flim)

        def filter(get_frame, t):
            frame = get_frame(t)
            if cupy_utils.is_cuda_array(frame):
                gpu_fn = getattr(self.other_clip, "_gpu_frame_function", None)
                if gpu_fn is not None:
                    try:
                        other = gpu_fn(t)
                        return _min(frame, other)
                    except Exception:
                        pass
            other = self.other_clip.get_frame(t)
            return _min(frame, other)

        return clip.transform(filter)
