"""Image sequencing clip tests meant to be run with pytest."""

import os

import numpy as np

import pytest

from moviepy.audio.AudioClip import (
    AudioArrayClip,
    AudioClip,
    CompositeAudioClip,
    concatenate_audioclips,
)
from moviepy.audio.io.AudioFileClip import AudioFileClip


def test_audioclip(util, mono_wave):
    filename = os.path.join(util.TMP_DIR, "audioclip.mp3")
    audio = AudioClip(mono_wave(440), duration=2, fps=22050)
    audio.write_audiofile(filename, bitrate="16", logger=None)

    assert os.path.exists(filename)

    AudioFileClip(filename)

    # TODO Write better tests; find out why the following fail
    # assert clip.duration == 2
    # assert clip.fps == 22050
    # assert clip.reader.bitrate == 16


def test_audioclip_io(util):
    filename = os.path.join(util.TMP_DIR, "random.wav")

    # Generate a random audio clip of 4.989 seconds at 44100 Hz,
    # and save it to a file.
    input_array = np.random.random((220000, 2)) * 1.98 - 0.99
    clip = AudioArrayClip(input_array, fps=44100)
    clip.write_audiofile(filename, logger=None)
    # Load the clip.
    # The loaded clip will be slightly longer because the duration is rounded
    # up to 4.99 seconds.
    # Verify that the extra frames are all zero, and the remainder is identical
    # to the original signal.
    clip = AudioFileClip(filename)
    output_array = clip.to_soundarray()
    np.testing.assert_array_almost_equal(
        output_array[: len(input_array)], input_array, decimal=4
    )
    assert (output_array[len(input_array) :] == 0).all()


def test_concatenate_audioclips_render(util, mono_wave):
    """Concatenated AudioClips through ``concatenate_audioclips`` should return
    a clip that can be rendered to a file.
    """
    filename = os.path.join(util.TMP_DIR, "concatenate_audioclips.mp3")

    clip_440 = AudioClip(mono_wave(440), duration=0.01, fps=44100)
    clip_880 = AudioClip(mono_wave(880), duration=0.000001, fps=22050)

    concat_clip = concatenate_audioclips((clip_440, clip_880))
    concat_clip.write_audiofile(filename, logger=None)

    assert concat_clip.duration == clip_440.duration + clip_880.duration


def test_concatenate_audioclips_CompositeAudioClip():
    """Concatenated AudioClips through ``concatenate_audioclips`` should return
    a CompositeAudioClip whose attributes should be consistent:

    - Returns CompositeAudioClip.
    - Their fps is taken from the maximum of their audios.
    - Audios are placed one after other:
      - Duration is the sum of their durations.
      - Ends are the accumulated sum of their durations.
      - Starts are the accumulated sum of their durations, but first start is 0
      and latest is ignored.
    - Channels are the max channels of their clips.
    """
    frequencies = [440, 880, 1760]
    durations = [2, 5, 1]
    fpss = [44100, 22050, 11025]

    clips = [
        AudioClip(
            lambda t: [np.sin(frequency * 2 * np.pi * t)], duration=duration, fps=fps
        )
        for frequency, duration, fps in zip(frequencies, durations, fpss)
    ]

    concat_clip = concatenate_audioclips(clips)

    # should return a CompositeAudioClip
    assert isinstance(concat_clip, CompositeAudioClip)

    # fps of the greatest fps passed into it
    assert concat_clip.fps == 44100

    # audios placed on after other
    assert concat_clip.duration == sum(durations)
    assert list(concat_clip.ends) == list(np.cumsum(durations))
    assert list(concat_clip.starts), list(np.cumsum([0, *durations[:-1]]))

    # channels are maximum number of channels of the clips
    assert concat_clip.nchannels == max(clip.nchannels for clip in clips)


def test_CompositeAudioClip_by__init__():
    """The difference between the CompositeAudioClip returned by
    ``concatenate_audioclips`` and a CompositeAudioClip created using the class
    directly, is that audios in ``concatenate_audioclips`` are played one after
    other and AudioClips passed to CompositeAudioClip can be played at different
    times, it depends on their ``start`` attributes.
    """
    frequencies = [440, 880, 1760]
    durations = [2, 5, 1]
    fpss = [44100, 22050, 11025]
    starts = [0, 1, 2]

    clips = [
        AudioClip(
            lambda t: [np.sin(frequency * 2 * np.pi * t)], duration=duration, fps=fps
        ).with_start(start)
        for frequency, duration, fps, start in zip(frequencies, durations, fpss, starts)
    ]

    compound_clip = CompositeAudioClip(clips)

    # should return a CompositeAudioClip
    assert isinstance(compound_clip, CompositeAudioClip)

    # fps of the greatest fps passed into it
    assert compound_clip.fps == 44100

    # duration depends on clips starts and durations
    ends = [start + duration for start, duration in zip(starts, durations)]
    assert compound_clip.duration == max(ends)
    assert list(compound_clip.ends) == ends
    assert list(compound_clip.starts) == starts

    # channels are maximum number of channels of the clips
    assert compound_clip.nchannels == max(clip.nchannels for clip in clips)


def test_concatenate_audioclip_with_audiofileclip(util, stereo_wave):
    clip1 = AudioClip(
        stereo_wave(left_freq=440, right_freq=880),
        duration=1,
        fps=44100,
    )
    clip2 = AudioFileClip("media/crunching.mp3")

    concat_clip = concatenate_audioclips((clip1, clip2))
    concat_clip.write_audiofile(
        os.path.join(util.TMP_DIR, "concat_clip_with_file_audio.mp3"),
        logger=None,
    )

    assert concat_clip.duration == clip1.duration + clip2.duration


def test_concatenate_audiofileclips(util):
    clip1 = AudioFileClip("media/crunching.mp3").subclipped(1, 4)

    # Checks it works with videos as well
    clip2 = AudioFileClip("media/big_buck_bunny_432_433.webm")
    concat_clip = concatenate_audioclips((clip1, clip2))

    concat_clip.write_audiofile(
        os.path.join(util.TMP_DIR, "concat_audio_file.mp3"),
        logger=None,
    )

    assert concat_clip.duration == clip1.duration + clip2.duration


def test_audioclip_mono_max_volume(mono_wave):
    clip = AudioClip(mono_wave(440), duration=1, fps=44100)
    max_volume = clip.max_volume()
    assert isinstance(max_volume, float)
    assert max_volume > 0


@pytest.mark.parametrize(("nchannels"), (2, 4, 8, 16))
@pytest.mark.parametrize(("channel_muted"), ("left", "right"))
def test_audioclip_stereo_max_volume(nchannels, channel_muted):
    def frame_function(t):
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

    clip = AudioClip(frame_function, fps=44100, duration=1)
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
