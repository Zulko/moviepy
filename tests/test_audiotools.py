"""Audio tools tests."""

import pytest

from moviepy.audio.AudioClip import AudioClip, CompositeAudioClip
from moviepy.audio.fx.multiply_volume import multiply_volume
from moviepy.audio.tools.cuts import find_audio_period
from moviepy.video.fx.loop import loop

from tests.test_helper import get_mono_wave, get_stereo_wave


@pytest.mark.parametrize("wave", ("mono", "stereo"))
def test_find_audio_period(wave):
    if wave == "mono":
        wave1 = get_mono_wave(freq=400)
        wave2 = get_mono_wave(freq=100)
    else:
        wave1 = get_stereo_wave(left_freq=400, right_freq=220)
        wave2 = get_stereo_wave(left_freq=100, right_freq=200)
    clip = CompositeAudioClip(
        [
            AudioClip(make_frame=wave1, duration=0.3, fps=22050),
            multiply_volume(
                AudioClip(make_frame=wave2, duration=0.3, fps=22050),
                0,
                end_time=0.1,
            ),
        ]
    )
    loop_clip = loop(clip, 4)
    assert round(find_audio_period(loop_clip), 6) == pytest.approx(0.29932, 0.1)


if __name__ == "__main__":
    pytest.main()
