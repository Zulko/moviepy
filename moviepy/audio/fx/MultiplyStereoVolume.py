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
        if clip.nchannels == 1:
            volume = self.left if self.left is not None else self.right
        else:
            volume = np.array(
                [self.left if i % 2 == 0 else self.right for i in range(clip.nchannels)]
            )

        def stereo_volume(get_frame, t):
            # Broadcast over channels for scalar samples and batches alike.
            # Out-of-place multiplication preserves shared or read-only frames.
            return np.asarray(get_frame(t)) * volume

        return clip.transform(stereo_volume)
