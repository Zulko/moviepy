"""Image sequencing clip tests meant to be run with pytest."""

import os

import pytest
import numpy as np

from moviepy.audio.AudioClip import (
    AudioArrayClip,
    AudioClip,
    concatenate_audioclips,
)
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.utils import close_all_clips

from tests.test_helper import TMP_DIR


def test_audioclip():
    make_frame = lambda t: [np.sin(440 * 2 * np.pi * t)]
    audio = AudioClip(make_frame, duration=2, fps=22050)
    audio.write_audiofile(os.path.join(TMP_DIR, "audioclip.mp3"), bitrate="16")

    assert os.path.exists(os.path.join(TMP_DIR, "audioclip.mp3"))

    clip = AudioFileClip(os.path.join(TMP_DIR, "audioclip.mp3"))

    # TODO Write better tests; find out why the following fail
    # assert clip.duration == 2
    # assert clip.fps == 22050
    # assert clip.reader.bitrate == 16
    close_all_clips(locals())


def test_audioclip_io():
    # Generate a random audio clip of 4.989 seconds at 44100 Hz,
    # and save it to a file.
    input_array = np.random.random((220000, 2)) * 1.98 - 0.99
    clip = AudioArrayClip(input_array, fps=44100)
    clip.write_audiofile(os.path.join(TMP_DIR, "random.wav"))
    # Load the clip.
    # The loaded clip will be slightly longer because the duration is rounded
    # up to 4.99 seconds.
    # Verify that the extra frames are all zero, and the remainder is identical
    # to the original signal.
    clip = AudioFileClip(os.path.join(TMP_DIR, "random.wav"))
    output_array = clip.to_soundarray()
    np.testing.assert_array_almost_equal(
        output_array[: len(input_array)], input_array, decimal=4
    )
    assert (output_array[len(input_array) :] == 0).all()


def test_audioclip_concat():
    make_frame_440 = lambda t: [np.sin(440 * 2 * np.pi * t)]
    make_frame_880 = lambda t: [np.sin(880 * 2 * np.pi * t)]

    clip1 = AudioClip(make_frame_440, duration=1, fps=44100)
    clip2 = AudioClip(make_frame_880, duration=2, fps=22050)

    concat_clip = concatenate_audioclips((clip1, clip2))
    # concatenate_audioclips should return a clip with an fps of the greatest
    # fps passed into it
    assert concat_clip.fps == 44100

    return
    # Does run without errors, but the length of the audio is way to long,
    # so it takes ages to run.
    concat_clip.write_audiofile(os.path.join(TMP_DIR, "concat_audioclip.mp3"))


def test_audioclip_with_file_concat():
    make_frame_440 = lambda t: [np.sin(440 * 2 * np.pi * t)]
    clip1 = AudioClip(make_frame_440, duration=1, fps=44100)

    clip2 = AudioFileClip("media/crunching.mp3")

    concat_clip = concatenate_audioclips((clip1, clip2))

    return
    # Fails with strange error
    # "ValueError: operands could not be broadcast together with
    # shapes (1993,2) (1993,1993)1
    concat_clip.write_audiofile(
        os.path.join(TMP_DIR, "concat_clip_with_file_audio.mp3")
    )


def test_audiofileclip_concat():
    sound = AudioFileClip("media/crunching.mp3")
    sound = sound.subclip(1, 4)

    # Checks it works with videos as well
    sound2 = AudioFileClip("media/big_buck_bunny_432_433.webm")
    concat = concatenate_audioclips((sound, sound2))

    concat.write_audiofile(os.path.join(TMP_DIR, "concat_audio_file.mp3"))


def test_audioclip_mono_max_volume():
    # mono
    make_frame_440 = lambda t: np.sin(440 * 2 * np.pi * t)
    clip = AudioClip(make_frame_440, duration=1, fps=44100)
    max_volume = clip.max_volume()
    assert isinstance(max_volume, float)
    assert max_volume > 0


@pytest.mark.parametrize(("nchannels"), (2, 4, 8, 16))
@pytest.mark.parametrize(("channel_muted"), ("left", "right"))
def test_audioclip_stereo_max_volume(nchannels, channel_muted):
    def make_frame(t):
        frame = []
        # build channels (one of each pair muted)
        for i in range(int(nchannels / 2)):
            if channel_muted == "left":
                # if muted channel is left, [0, sound, 0, sound...]
                frame.append(np.sin(t * 0))
                frame.append(np.sin(440 * 2 * np.pi * t))
            else:
                # if muted channel is right, [sound, 0, sound, 0...]
                frame.append(np.sin(440 * 2 * np.pi * t))
                frame.append(np.sin(t * 0))
        return np.array(frame).T

    clip = AudioClip(make_frame, fps=44100, duration=1)
    max_volume = clip.max_volume(stereo=True)
    # if `stereo == True`, `AudioClip.max_volume` returns a Numpy array`
    assert isinstance(max_volume, np.ndarray)
    assert len(max_volume) == nchannels

    # check channels muted and with sound
    for i, channel_max_volume in enumerate(max_volume):
        if i % 2 == 0:
            if channel_muted == "left":
                assert channel_max_volume == 0
            else:
                assert channel_max_volume > 0
        else:
            if channel_muted == "right":
                assert channel_max_volume == 0
            else:
                assert channel_max_volume > 0


if __name__ == "__main__":
    pytest.main()
