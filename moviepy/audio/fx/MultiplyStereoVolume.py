from dataclasses import dataclass

import numpy as np

from moviepy.Clip import Clip
from moviepy.decorators import audio_video_effect
from moviepy.Effect import Effect


@dataclass
class MultiplyStereoVolume(Effect):
    """For a stereo audioclip, this function enables to change the volume
    of the left and right channel separately (with the factors `left`
    and `right`). Makes a stereo audio clip in which the volume of left
    and right is controllable.

    Examples
    --------

    .. code:: python

        from moviepy import AudioFileClip
        music = AudioFileClip('music.ogg')
        # mutes left channel
        audio_r = music.with_effects([afx.MultiplyStereoVolume(left=0, right=1)])
        # halves audio volume
        audio_h = music.with_effects([afx.MultiplyStereoVolume(left=0.5, right=0.5)])
    """

    left: float = 1
    right: float = 1

    @audio_video_effect
    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""

        def stereo_volume(get_frame, t):
            frame = get_frame(t)
            left = self.left if self.left is not None else self.right
            right = self.right if self.right is not None else self.left
            if frame is None:
                return frame

            # Historical MoviePy audio frame_functions may return a list/tuple of
            # per-channel arrays (or scalars). Normalize that efficiently.
            if isinstance(frame, (list, tuple)):
                # Keep list semantics for mono clips for backward compatibility:
                # list * int replicates channels (as in older behavior/tests).
                if len(frame) == 1:
                    scale = left
                    if isinstance(scale, (int, np.integer)):
                        return list(frame) * int(scale)
                    return [np.asarray(frame[0]) * scale]

                out = []
                for i, ch in enumerate(frame):
                    scale = left if (i % 2 == 0) else right
                    out.append(np.asarray(ch) * scale)
                return out

            # Support both scalar-time frames (shape (C,)) and chunk frames
            # (shape (N, C)).
            if getattr(frame, "ndim", 0) == 1:
                if frame.shape[0] == 1:
                    frame *= left
                else:
                    frame[::2] *= left
                    frame[1::2] *= right
            else:
                if frame.shape[1] == 1:
                    frame *= left
                else:
                    frame[:, ::2] *= left
                    frame[:, 1::2] *= right
            return frame

        return clip.transform(stereo_volume)
