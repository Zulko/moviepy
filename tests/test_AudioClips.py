# -*- coding: utf-8 -*-
"""Image sequencing clip tests meant to be run with pytest."""
import os
import sys

from numpy import sin, pi
import pytest

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import AudioClip, concatenate_audioclips, CompositeAudioClip
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos

from .test_helper import TMP_DIR

def test_audio_coreader():
    if sys.platform.startswith("win"):
        pytest.skip("Temporarily skipping on windows because otherwise test suite fails with Invalid Handle Error")

    sound = AudioFileClip("media/crunching.mp3")
    sound = sound.subclip(1, 4)
    sound2 = AudioFileClip("media/crunching.mp3")
    sound2.write_audiofile(os.path.join(TMP_DIR, "coreader.mp3"))

def test_audioclip():
    make_frame = lambda t: [sin(440 * 2 * pi * t)]
    clip = AudioClip(make_frame, duration=2, fps=22050)
    clip.write_audiofile(os.path.join(TMP_DIR, "audioclip.mp3"))

def test_audioclip_concat():
    if sys.platform.startswith("win"):
        pytest.skip("Temporarily skipping on windows because otherwise test suite fails with Invalid Handle Error")

    make_frame_440 = lambda t: [sin(440 * 2 * pi * t)]
    make_frame_880 = lambda t: [sin(880 * 2 * pi * t)]

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
    if sys.platform.startswith("win"):
        pytest.skip("Temporarily skipping on windows because otherwise test suite fails with Invalid Handle Error")

    make_frame_440 = lambda t: [sin(440 * 2 * pi * t)]
    clip1 = AudioClip(make_frame_440, duration=1, fps=44100)

    clip2 = AudioFileClip("media/crunching.mp3")

    concat_clip = concatenate_audioclips((clip1, clip2))

    return
    # Fails with strange error
    # "ValueError: operands could not be broadcast together with
    # shapes (1993,2) (1993,1993)1
    concat_clip.write_audiofile(os.path.join(TMP_DIR, "concat_clip_with_file_audio.mp3"))


def test_audiofileclip_concat():
    if sys.platform.startswith("win"):
        pytest.skip("Temporarily skipping on windows because otherwise test suite fails with Invalid Handle Error")

    sound = AudioFileClip("media/crunching.mp3")
    sound = sound.subclip(1, 4)

    # Checks it works with videos as well
    sound2 = AudioFileClip("media/big_buck_bunny_432_433.webm")
    concat = concatenate_audioclips((sound, sound2))

    concat.write_audiofile(os.path.join(TMP_DIR, "concat_audio_file.mp3"))


def test_write_audiofile_default():
    clip = AudioFileClip("media/crunching.mp3")
    location = os.path.join(TMP_DIR, "test_write_audiofile_default.ogg")
    clip.write_audiofile(location)
    d=ffmpeg_parse_infos(location)
    assert d['audio_found']
    assert not d['video_found']


def test_write_audiofile_with_silent_video():
    source_video = "media/clip1024.flv"
    d=ffmpeg_parse_infos(source_video)
    assert not d['audio_found']
    clip = AudioFileClip("media/crunching.mp3")
    location = os.path.join(TMP_DIR, "test_write_audiofile_with_silent_video.flv")
    clip.write_audiofile(location, video=source_video)
    d=ffmpeg_parse_infos(location)
    assert d['audio_found']
    assert d['video_found']


def test_write_audiofile_and_change_video_codec():
    source_video = "media/clip1024.flv"
    d=ffmpeg_parse_infos(source_video)
    assert not d['audio_found']
    clip = AudioFileClip("media/crunching.mp3")
    location = os.path.join(TMP_DIR, "test_write_audiofile_and_change_video_codec.webm")
    clip.write_audiofile(location, video=source_video, video_codec='libvpx')
    d=ffmpeg_parse_infos(location)
    assert d['audio_found']
    assert d['video_found']


def test_write_audiofile_with_video():
    #
    # THIS SHOULD CHECK STREAMS IN DETAIL BUT OUR READER DOES NOT EXPOSE THAT INFO
    #   related:
    #       - https://github.com/Zulko/moviepy/issues/249
    #       - https://github.com/Zulko/moviepy/issues/590
    #       - https://github.com/imageio/imageio-ffmpeg/issues/23
    #
    source_video = "media/big_buck_bunny_432_433.webm"
    d=ffmpeg_parse_infos(source_video)
    assert d['audio_found']
    clip = AudioFileClip("media/crunching.mp3")
    location = os.path.join(TMP_DIR, "test_write_audiofile_with_video.ogg")
    clip.write_audiofile(location)
    d=ffmpeg_parse_infos(location)
    assert d['audio_found']
    assert d['video_found']
    

if __name__ == "__main__":
    pytest.main()
