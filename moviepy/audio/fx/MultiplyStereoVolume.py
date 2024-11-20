from dataclasses import dataclass

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

    >>> from moviepy import AudioFileClip
    >>> music = AudioFileClip('music.ogg')
    >>> # mutes left channel
    >>> audio_r = music.with_effects([afx.MultiplyStereoVolume(left=0, right=1)])
    >>> # halves audio volume
    >>> audio_h = music.with_effects([afx.MultiplyStereoVolume(left=0.5, right=0.5)])
    """

    left: float = 1
    right: float = 1

    @audio_video_effect
    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""

        def stereo_volume(get_frame, t):
            frame = get_frame(t)
            if len(frame) == 1:  # mono
                frame *= self.left if self.left is not None else self.right
            else:  # stereo, stereo surround...
                for i in range(len(frame[0])):  # odd channels are left
                    frame[:, i] *= self.left if i % 2 == 0 else self.right
            return frame

        return clip.transform(stereo_volume)
