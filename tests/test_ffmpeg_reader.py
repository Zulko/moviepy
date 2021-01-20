"""FFmpeg reader tests meant to be run with pytest."""

import os
import subprocess

import pytest
import numpy as np

from moviepy.config import FFMPEG_BINARY
from moviepy.audio.AudioClip import AudioClip
from moviepy.video.VideoClip import BitmapClip
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos, FFMPEG_VideoReader
from moviepy.utils import close_all_clips

from tests.test_helper import TMP_DIR


def test_ffmpeg_parse_infos():
    d = ffmpeg_parse_infos("media/big_buck_bunny_432_433.webm")
    assert d["duration"] == 1.0
    assert d["audio_fps"] == 44100

    d = ffmpeg_parse_infos("media/pigs_in_a_polka.gif")
    assert d["video_size"] == [314, 273]
    assert d["duration"] == 3.0
    assert not d["audio_found"]

    d = ffmpeg_parse_infos("media/video_with_failing_audio.mp4")
    assert d["audio_found"]
    assert d["audio_fps"] == 44100
    assert d["audio_bitrate"] == 127

    d = ffmpeg_parse_infos("media/crunching.mp3")
    assert d["audio_found"]
    assert d["audio_fps"] == 48000
    assert d["metadata"]["artist"] == "SoundJay.com Sound Effects"

    d = ffmpeg_parse_infos("media/sintel_with_14_chapters.mp4")
    assert d["audio_found"]
    assert d["video_found"]
    assert d["audio_bitrate"]
    assert d["video_bitrate"]


def test_ffmpeg_parse_infos_video_nframes():
    d = ffmpeg_parse_infos("media/big_buck_bunny_0_30.webm")
    assert d["video_n_frames"] == 720

    d = ffmpeg_parse_infos("media/bitmap.mp4")
    assert d["video_n_frames"] == 5


@pytest.mark.parametrize(
    ("decode_file", "expected_duration"),
    (
        (False, 30),
        (True, 30.02),
    ),
    ids=(
        "decode_file=False",
        "decode_file=True",
    ),
)
def test_ffmpeg_parse_infos_decode_file(decode_file, expected_duration):
    """Test `decode_file` argument of `ffmpeg_parse_infos` function."""
    d = ffmpeg_parse_infos("media/big_buck_bunny_0_30.webm", decode_file=decode_file)
    assert d["duration"] == expected_duration

    # check metadata is fine
    assert len(d["metadata"]) == 1

    # check input
    assert len(d["inputs"]) == 1

    # check streams
    streams = d["inputs"][0]["streams"]
    assert len(streams) == 2
    assert streams[0]["stream_type"] == "video"
    assert streams[0]["stream_number"] == 0
    assert streams[0]["fps"] == 24
    assert streams[0]["size"] == [1280, 720]
    assert streams[0]["default"] is True
    assert streams[0]["language"] is None

    assert streams[1]["stream_type"] == "audio"
    assert streams[1]["stream_number"] == 1
    assert streams[1]["fps"] == 44100
    assert streams[1]["default"] is True
    assert streams[1]["language"] is None


def test_ffmpeg_parse_infos_multiple_audio_streams():
    """Check that ``ffmpeg_parse_infos`` can parse multiple audio streams."""
    # Create two mono audio files
    clip_440_filepath = os.path.join(
        TMP_DIR, "ffmpeg_parse_infos_multiple_streams_440.mp3"
    )
    clip_880_filepath = os.path.join(
        TMP_DIR, "ffmpeg_parse_infos_multiple_streams_880.mp3"
    )
    multiple_streams_filepath = os.path.join(
        TMP_DIR, "ffmpeg_parse_infos_multiple_streams.mp4"
    )

    make_frame_440 = lambda t: np.array(
        [
            np.sin(440 * 2 * np.pi * t),
        ]
    )
    make_frame_880 = lambda t: np.array(
        [
            np.sin(880 * 2 * np.pi * t),
        ]
    )

    clip_440 = AudioClip(make_frame_440, fps=22050, duration=0.01)
    clip_880 = AudioClip(make_frame_880, fps=22050, duration=0.01)
    clip_440.write_audiofile(clip_440_filepath)
    clip_880.write_audiofile(clip_880_filepath)

    # create a MP4 file with multiple streams
    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-i",
        clip_440_filepath,
        "-i",
        clip_880_filepath,
        "-map",
        "0:a:0",
        "-map",
        "0:a:0",
        multiple_streams_filepath,
    ]
    with open(os.devnull, "w") as stderr:
        subprocess.check_call(cmd, stderr=stderr)

    # check that `ffmpeg_parse_infos` can parse all the streams data
    d = ffmpeg_parse_infos(multiple_streams_filepath)

    # number of inputs and streams
    assert len(d["inputs"]) == 1
    assert len(d["inputs"][0]["streams"]) == 2

    default_stream = d["inputs"][0]["streams"][0]
    ignored_stream = d["inputs"][0]["streams"][1]

    # default, only the first
    assert default_stream["default"]
    assert not ignored_stream["default"]

    # streams and inputs numbers
    assert default_stream["stream_number"] == 0
    assert ignored_stream["stream_number"] == 1
    assert default_stream["input_number"] == 0
    assert ignored_stream["input_number"] == 0

    # stream type
    assert default_stream["stream_type"] == "audio"
    assert ignored_stream["stream_type"] == "audio"

    # cleanup
    for filepath in [clip_440_filepath, clip_880_filepath, multiple_streams_filepath]:
        os.remove(filepath)
    close_all_clips(locals())


def test_ffmpeg_parse_infos_metadata():
    """Check that `ffmpeg_parse_infos` is able to retrieve metadata from files."""
    filepath = os.path.join(TMP_DIR, "ffmpeg_parse_infos_metadata.mkv")
    if os.path.isfile(filepath):
        os.remove(filepath)

    # create video with 2 streams, video and audio
    audioclip = AudioClip(
        lambda t: np.sin(440 * 2 * np.pi * t), fps=22050
    ).with_duration(1)
    videoclip = BitmapClip([["RGB"]], fps=1).with_duration(1).with_audio(audioclip)

    # build metadata key-value pairs which will be passed to ``ffmpeg_params``
    # argument of ``videoclip.write_videofile``
    metadata = {
        "file": {
            "title": "Fóò",
            "comment": "bar",
            "description": "BAZ",
            "synopsis": "Testing",
        },
        "video": {
            "author": "Querty",
            "title": "hello",
            "description": "asdf",
        },
        "audio": {"track": "1", "title": "wtr", "genre": "lilihop"},
    }

    ffmpeg_params = []
    for metadata_type, data in metadata.items():
        option = "-metadata"
        if metadata_type in ["video", "audio"]:
            option += ":s:%s:0" % ("v" if metadata_type == "video" else "a")
        for field, value in data.items():
            ffmpeg_params.extend([option, f"{field}={value}"])

    languages = {
        "audio": "eng",
        "video": "spa",
    }
    ffmpeg_params.extend(
        [
            "-metadata:s:a:0",
            "language=" + languages["audio"],
            "-metadata:s:v:0",
            "language=" + languages["video"],
        ]
    )

    # create file with metadata included
    videoclip.write_videofile(filepath, codec="libx264", ffmpeg_params=ffmpeg_params)

    # get information about created file
    d = ffmpeg_parse_infos(filepath)

    def get_value_from_dict_using_lower_key(field, dictionary):
        """Obtains a value from a dictionary using a key, no matter if the key
        is uppercased in the dictionary. This function is needed because
        some media containers convert to uppercase metadata field names.
        """
        value = None
        for d_field, d_value in dictionary.items():
            if str(d_field).lower() == field:
                value = d_value
                break
        return value

    # assert file metadata
    for field, value in metadata["file"].items():
        assert get_value_from_dict_using_lower_key(field, d["metadata"]) == value

    # assert streams metadata
    streams = {"audio": None, "video": None}
    for stream in d["inputs"][0]["streams"]:
        streams[stream["stream_type"]] = stream

    for stream_type, stream in streams.items():
        for field, value in metadata[stream_type].items():
            assert (
                get_value_from_dict_using_lower_key(field, stream["metadata"]) == value
            )

    # assert stream languages
    for stream_type, stream in streams.items():
        assert stream["language"] == languages[stream_type]

    os.remove(filepath)

    close_all_clips(locals())


def test_ffmpeg_parse_infos_chapters():
    """Check that `ffmpeg_parse_infos` can parse chapters with their metadata."""
    d = ffmpeg_parse_infos("media/sintel_with_14_chapters.mp4")

    chapters = d["inputs"][0]["chapters"]

    num_chapters_expected = 14

    assert len(chapters) == num_chapters_expected
    for num in range(0, len(chapters)):
        assert chapters[num]["chapter_number"] == num
        assert chapters[num]["end"] == (num + 1) / 10
        assert chapters[num]["start"] == num / 10
        assert chapters[num]["metadata"]["title"]
        assert isinstance(chapters[num]["metadata"]["title"], str)


def test_sequential_frame_pos():
    """test_video.mp4 contains 5 frames at 1 fps.
    Each frame is 1x1 pixels and the sequence is Red, Green, Blue, Black, White.
    The rgb values are not pure due to compression."""
    reader = FFMPEG_VideoReader("media/test_video.mp4")
    assert reader.pos == 1

    # Get first frame
    frame_1 = reader.get_frame(0)
    assert reader.pos == 1
    assert np.array_equal(frame_1, [[[254, 0, 0]]])

    # Get a specific sequential frame
    frame_2 = reader.get_frame(1)
    assert reader.pos == 2
    assert np.array_equal(frame_2, [[[0, 255, 1]]])

    # Get next frame. Note `.read_frame()` instead of `.get_frame()`
    frame_3 = reader.read_frame()
    assert reader.pos == 3
    assert np.array_equal(frame_3, [[[0, 0, 255]]])

    # Skip a frame
    skip_frame = reader.get_frame(4)
    assert reader.pos == 5
    assert np.array_equal(skip_frame, [[[255, 255, 255]]])


def test_unusual_order_frame_pos():
    reader = FFMPEG_VideoReader("media/test_video.mp4")
    assert reader.pos == 1

    # Go straight to end
    end_frame = reader.get_frame(4)
    assert reader.pos == 5
    assert np.array_equal(end_frame, [[[255, 255, 255]]])

    # Repeat the previous frame
    second_end_frame = reader.get_frame(4)
    assert reader.pos == 5
    assert np.array_equal(second_end_frame, [[[255, 255, 255]]])

    # Go backwards
    previous_frame = reader.get_frame(3)
    assert reader.pos == 4
    assert np.array_equal(previous_frame, [[[0, 0, 0]]])

    # Go back to start
    start_frame = reader.get_frame(0)
    assert reader.pos == 1
    assert np.array_equal(start_frame, [[[254, 0, 0]]])


def test_large_skip_frame_pos():
    reader = FFMPEG_VideoReader("media/big_buck_bunny_0_30.webm")
    assert reader.fps == 24

    # 10 sec * 24 fps = 240 frames
    reader.get_frame(240 // 24)
    assert reader.pos == 241

    reader.get_frame(719 / 24)
    assert reader.pos == 720

    # Go backwards
    reader.get_frame(120 // 24)
    assert reader.pos == 121


def test_large_small_skip_equal():
    """Get the 241st frame of the file in 4 different ways:
    Reading every frame, Reading every 24th frame, Jumping straight there"""
    sequential_reader = FFMPEG_VideoReader("media/big_buck_bunny_0_30.webm")
    small_skip_reader = FFMPEG_VideoReader("media/big_buck_bunny_0_30.webm")
    large_skip_reader = FFMPEG_VideoReader("media/big_buck_bunny_0_30.webm")
    assert small_skip_reader.fps == large_skip_reader.fps == sequential_reader.fps == 24

    # Read every frame sequentially
    for t in np.arange(0, 10, 1 / 24):
        sequential_reader.get_frame(t)
    sequential_final_frame = sequential_reader.get_frame(10)

    # Read in increments of 24 frames
    for t in range(10):
        small_skip_reader.get_frame(t)
    small_skip_final_frame = small_skip_reader.get_frame(10)

    # Jumps straight forward 240 frames. This is greater than 100 so it uses
    # FFmpeg to reseek at the right position.
    large_skip_final_frame = large_skip_reader.get_frame(10)

    assert (
        sequential_reader.pos == small_skip_reader.pos == large_skip_reader.pos == 241
    )

    # All frames have gone forward an equal amount, so should be equal
    assert np.array_equal(sequential_final_frame, small_skip_final_frame)
    assert np.array_equal(small_skip_final_frame, large_skip_final_frame)


def test_seeking_beyond_file_end():
    reader = FFMPEG_VideoReader("media/test_video.mp4")
    frame_1 = reader.get_frame(0)

    with pytest.warns(UserWarning, match="Using the last valid frame instead"):
        end_of_file_frame = reader.get_frame(5)
    assert np.array_equal(frame_1, end_of_file_frame)
    assert reader.pos == 6

    # Try again with a jump larger than 100 frames
    # (which triggers different behaivour in `.get_frame()`
    reader = FFMPEG_VideoReader("media/big_buck_bunny_0_30.webm")
    frame_1 = reader.get_frame(0)

    with pytest.warns(UserWarning, match="Using the last valid frame instead"):
        end_of_file_frame = reader.get_frame(30)
    assert np.array_equal(frame_1, end_of_file_frame)
    assert reader.pos == 30 * 24 + 1


if __name__ == "__main__":
    pytest.main()
