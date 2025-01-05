"""FFmpeg reader tests meant to be run with pytest."""

import os
import subprocess
import time

import numpy as np

import pytest

from moviepy.audio.AudioClip import AudioClip
from moviepy.config import FFMPEG_BINARY
from moviepy.video.compositing.CompositeVideoClip import clips_array
from moviepy.video.io.ffmpeg_reader import (
    FFMPEG_VideoReader,
    FFmpegInfosParser,
    ffmpeg_parse_infos,
)
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import BitmapClip, ColorClip


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


def test_ffmpeg_parse_infos_multiple_audio_streams(util, mono_wave):
    """Check that ``ffmpeg_parse_infos`` can parse multiple audio streams."""
    # Create two mono audio files
    clip_440_filepath = os.path.join(
        util.TMP_DIR, "ffmpeg_parse_infos_multiple_streams_440.mp3"
    )
    clip_880_filepath = os.path.join(
        util.TMP_DIR, "ffmpeg_parse_infos_multiple_streams_880.mp3"
    )
    multiple_streams_filepath = os.path.join(
        util.TMP_DIR, "ffmpeg_parse_infos_multiple_streams.mp4"
    )

    clip_440 = AudioClip(mono_wave(440), fps=22050, duration=0.01)
    clip_880 = AudioClip(mono_wave(880), fps=22050, duration=0.01)
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


def test_ffmpeg_parse_infos_metadata(util, mono_wave):
    """Check that `ffmpeg_parse_infos` is able to retrieve metadata from files."""
    filepath = os.path.join(util.TMP_DIR, "ffmpeg_parse_infos_metadata.mkv")
    if os.path.isfile(filepath):
        os.remove(filepath)

    # create video with 2 streams, video and audio
    audioclip = AudioClip(mono_wave(440), fps=22050).with_duration(1)
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


def test_ffmpeg_parse_infos_metadata_with_attached_pic():
    """Check that the parser can parse audios with attached pictures.

    Currently, does not distinguish if the video found is an attached picture,
    this test serves mainly to ensure that #1487 issue does not happen again:
    """
    d = ffmpeg_parse_infos("media/with-attached-pic.mp3")

    assert d["audio_bitrate"] == 320
    assert d["audio_found"]
    assert d["audio_fps"] == 44100

    assert len(d["inputs"]) == 1
    streams = d["inputs"][0]["streams"]
    assert len(streams) == 2
    assert streams[0]["stream_type"] == "audio"
    assert streams[1]["stream_type"] == "video"

    assert len(d["metadata"].keys()) == 7


def test_ffmpeg_parse_video_rotation():
    d = ffmpeg_parse_infos("media/rotated-90-degrees.mp4")
    assert d["video_rotation"] == 90
    assert d["video_size"] == [1920, 1080]


def test_correct_video_rotation(util):
    """See https://github.com/Zulko/moviepy/pull/577"""
    clip = VideoFileClip("media/rotated-90-degrees.mp4").subclipped(0.2, 0.4)

    corrected_rotation_filename = os.path.join(
        util.TMP_DIR,
        "correct_video_rotation.mp4",
    )
    clip.write_videofile(corrected_rotation_filename)

    d = ffmpeg_parse_infos(corrected_rotation_filename)
    assert "video_rotation" not in d
    assert d["video_size"] == [1080, 1920]


def test_ffmpeg_parse_infos_multiline_metadata():
    """Check that the parser can parse multiline metadata values."""
    infos = """Input #0, mov,mp4,m4a,3gp,3g2,mj2, from '/home/110_PREV_FINAL.mov':
  Metadata:
    major_brand     : foo
    minor_version   : 537199360
    compatible_brands: bar
    creation_time   : 2999-08-12 09:00:01
    xmw             : <?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
                    : <second XML line">
                    :  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/22-rdf-syntax-ns#">
                    :   <rdf:Description rdf:about=""
                    :     xmlns:xmpMM="http://nowhere.ext"
                    :     xmlns:xmpDM="http://nowhere.ext/"
                    :     xmlns:stDim="http://nowhere.ext/Dimensions#"
                    :     xmlns:dc="http://nowhere.ext/dc/elements/1.1/"
                    :    xmpMM:DocumentID="xmw.did:39FA818BE85AE511B9009F953BF804AA"
                    :    xmwMM:InstanceID="xmw.iid:39FA818BE85AE511B9009F953BF804AA"
                    :    xmwDM:videoFrameRate="24.000000"
                    :    xmwDM:videoFieldOrder="Progressive"
                    :    xmwDM:videoPixelAspectRatio="1/1"
                    :    xmwDM:audioSampleRate="44100"
                    :    xmwDM:audioSampleType="16Int"
                    :    xmwDM:audioChannelType="Mono"
                    :    dc:format="QuickTimeline">
                    :    <xmwDM:startTimecode
                    :     xmwDM:timeValue="00:00:00:00"
                    :     xmwDM:timeFormat="24Timecode"/>
                    :    <xmwDM:altTimecode
                    :     xmwDM:timeValue="00:00:00:00"
                    :     xmwDM:timeFormat="24Timecode"/>
                    :    <xmwDM:videoFrameSize
                    :     stDim:w="768"
                    :     stDim:h="576"
                    :     stDim:unit="pixel"/>
                    :   </rdf:Description>
                    :  </rdf:RDF>
                    : </x:xmwmeta>
                    :
                    :
                    : <?xpacket end="w"?>
  Duration: 00:02:10.67, start: 0.000000, bitrate: 26287 kb/s
    Stream #0:0(eng): Video: mjpeg 768x576 26213 kb/s, 24 fps, 24 tbr (default)
    Metadata:
      creation_time   : 2015-09-14 14:57:32
      handler_name    : Foo
                      : Bar
      encoder         : Photo - JPEG
      timecode        : 00:00:00:00
    Stream #0:1(eng): Audio: aac (mp4a / 0x6), 44100 Hz, mono, fltp, 64 kb/s (default)
    Metadata:
      creation_time   : 2015-09-14 14:57:33
      handler_name    : Bar
                      : Foo
      timecode        : 00:00:00:00
    Stream #0:2(eng): Data: none (tmcd / 0x64636D74) (default)
    Metadata:
      creation_time   : 2015-09-14 14:58:24
      handler_name    : Baz
                      : Foo
      timecode        : 00:00:00:00
At least one output file must be specified
"""

    d = FFmpegInfosParser(infos, "foo.mkv").parse()

    # container data
    assert d["audio_bitrate"] == 64
    assert d["audio_found"] is True
    assert d["audio_fps"] == 44100
    assert d["duration"] == 130.67
    assert d["video_duration"] == 130.67
    assert d["video_found"] is True
    assert d["video_fps"] == 24
    assert d["video_n_frames"] == 3136
    assert d["video_size"] == [768, 576]
    assert d["start"] == 0
    assert d["default_audio_input_number"] == 0
    assert d["default_audio_stream_number"] == 1
    assert d["default_data_input_number"] == 0
    assert d["default_data_stream_number"] == 2
    assert d["default_video_input_number"] == 0
    assert d["default_video_stream_number"] == 0

    # container metadata
    assert d["metadata"]["compatible_brands"] == "bar"
    assert d["metadata"]["creation_time"] == "2999-08-12 09:00:01"
    assert d["metadata"]["major_brand"] == "foo"
    assert d["metadata"]["minor_version"] == "537199360"
    assert d["metadata"]["xmw"] == (
        """<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>
<second XML line">
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/22-rdf-syntax-ns#">
<rdf:Description rdf:about=""
xmlns:xmpMM="http://nowhere.ext"
xmlns:xmpDM="http://nowhere.ext/"
xmlns:stDim="http://nowhere.ext/Dimensions#"
xmlns:dc="http://nowhere.ext/dc/elements/1.1/"
xmpMM:DocumentID="xmw.did:39FA818BE85AE511B9009F953BF804AA"
xmwMM:InstanceID="xmw.iid:39FA818BE85AE511B9009F953BF804AA"
xmwDM:videoFrameRate="24.000000"
xmwDM:videoFieldOrder="Progressive"
xmwDM:videoPixelAspectRatio="1/1"
xmwDM:audioSampleRate="44100"
xmwDM:audioSampleType="16Int"
xmwDM:audioChannelType="Mono"
dc:format="QuickTimeline">
<xmwDM:startTimecode
xmwDM:timeValue="00:00:00:00"
xmwDM:timeFormat="24Timecode"/>
<xmwDM:altTimecode
xmwDM:timeValue="00:00:00:00"
xmwDM:timeFormat="24Timecode"/>
<xmwDM:videoFrameSize
stDim:w="768"
stDim:h="576"
stDim:unit="pixel"/>
</rdf:Description>
</rdf:RDF>
</x:xmwmeta>


<?xpacket end="w"?>"""
    )

    # streams
    assert len(d["inputs"]) == 1

    streams = d["inputs"][0]["streams"]
    assert len(streams) == 3

    # video stream
    assert streams[0]["default"] is True
    assert streams[0]["fps"] == 24
    assert streams[0]["input_number"] == 0
    assert streams[0]["language"] == "eng"
    assert streams[0]["stream_number"] == 0
    assert streams[0]["stream_type"] == "video"
    assert streams[0]["size"] == [768, 576]

    assert streams[0]["metadata"]["creation_time"] == "2015-09-14 14:57:32"
    assert streams[0]["metadata"]["encoder"] == "Photo - JPEG"
    assert streams[0]["metadata"]["handler_name"] == "Foo\nBar"
    assert streams[0]["metadata"]["timecode"] == "00:00:00:00"

    # audio stream
    assert streams[1]["default"] is True
    assert streams[1]["fps"] == 44100
    assert streams[1]["input_number"] == 0
    assert streams[1]["language"] == "eng"
    assert streams[1]["stream_number"] == 1
    assert streams[1]["stream_type"] == "audio"

    assert streams[1]["metadata"]["creation_time"] == "2015-09-14 14:57:33"
    assert streams[1]["metadata"]["timecode"] == "00:00:00:00"
    assert streams[1]["metadata"]["handler_name"] == "Bar\nFoo"

    # data stream
    assert streams[2]["default"] is True
    assert streams[2]["input_number"] == 0
    assert streams[2]["language"] == "eng"
    assert streams[2]["stream_number"] == 2
    assert streams[2]["stream_type"] == "data"

    assert streams[2]["metadata"]["creation_time"] == "2015-09-14 14:58:24"
    assert streams[2]["metadata"]["timecode"] == "00:00:00:00"
    assert streams[2]["metadata"]["handler_name"] == "Baz\nFoo"


def test_not_default_audio_stream_audio_bitrate():
    infos = """Input #0, avi, from 'file_example_AVI_1280_1_5MG.avi':
  Metadata:
    encoder         : Lavf57.19.100
  Duration: 00:00:30.61, start: 0.000000, bitrate: 387 kb/s
    Stream #0:0: Video: ..., 30 tbr, 60 tbc
    Stream #0:1: Audio: aac (LC) (...), 48000 Hz, stereo, fltp, 139 kb/s
"""

    d = FFmpegInfosParser(infos, "foo.avi").parse()
    assert d["audio_bitrate"] == 139


def test_stream_deidentation_not_raises_error():
    """Test libavformat reduced streams identation to 2 spaces.

    See https://github.com/FFmpeg/FFmpeg/commit/b7251aed
    """
    infos = """Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'clip.mp4':
  Metadata:
    major_brand     : isom
    minor_version   : 512
    compatible_brands: isomiso2avc1mp41
    encoder         : Lavf58.12.100
  Duration: 01:00:00.00, start: 0.000000, bitrate: 1222 kb/s
  Stream #0:0(und): Video: ..., 30 tbr, 60 tbc
    Metadata:
      handler_name    : VideoHandler
      vendor_id       : [0][0][0][0]
At least one output file must be specified"""

    d = FFmpegInfosParser(infos, "clip.mp4").parse()

    assert d
    assert len(d["inputs"][0]["streams"]) == 1


def test_stream_square_brackets():
    infos = """
Input #0, mpeg, from 'clip.mp4':
  Duration: 00:02:15.00, start: 52874.498178, bitrate: 266 kb/s
    Stream #0:0[0x1e0]: Video: ..., 25 tbr, 90k tbn, 50 tbc
    Stream #0:1[0x1c0]: Audio: mp2, 0 channels, s16p
At least one output file must be specified"""

    d = FFmpegInfosParser(infos, "clip.mp4").parse()

    assert d
    assert len(d["inputs"][0]["streams"]) == 2
    assert d["inputs"][0]["streams"][0]["language"] is None
    assert d["inputs"][0]["streams"][1]["language"] is None


def test_stream_square_brackets_and_language():
    infos = """
Input #0, mpeg, from 'clip.mp4':
  Duration: 00:02:15.00, start: 52874.498178, bitrate: 266 kb/s
    Stream #0:0[0x1e0](eng): Video: ..., 25 tbr, 90k tbn, 50 tbc
    Stream #0:1[0x1c0](und): Audio: mp2, 0 channels, s16p
At least one output file must be specified"""

    d = FFmpegInfosParser(infos, "clip.mp4").parse()

    assert d
    assert len(d["inputs"][0]["streams"]) == 2
    assert d["inputs"][0]["streams"][0]["language"] == "eng"
    assert d["inputs"][0]["streams"][1]["language"] is None


def test_stream_missing_audio_bitrate():
    infos = """
Input #0, mpeg, from 'clip.mp4':
  Duration: 00:02:15.00, start: 52874.498178, bitrate: 266 kb/s
    Stream #0:0[0x1e0]: Video: ..., 25 tbr, 90k tbn, 50 tbc
    Stream #0:1[0x1c0]: Audio: mp2, 0 channels, s16p
At least one output file must be specified"""

    d = FFmpegInfosParser(infos, "clip.mp4").parse()

    assert d
    assert len(d["inputs"][0]["streams"]) == 2
    assert d["audio_found"]
    assert d["audio_bitrate"] is None


def test_sequential_frame_pos():
    """test_video.mp4 contains 5 frames at 1 fps.
    Each frame is 1x1 pixels and the sequence is Red, Green, Blue, Black, White.
    The rgb values are not pure due to compression.
    """
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
    # (which triggers different behaviour in `.get_frame()`
    reader = FFMPEG_VideoReader("media/big_buck_bunny_0_30.webm")
    frame_1 = reader.get_frame(0)

    with pytest.warns(UserWarning, match="Using the last valid frame instead"):
        end_of_file_frame = reader.get_frame(30)
    assert np.array_equal(frame_1, end_of_file_frame)
    assert reader.pos == 30 * 24 + 1


def test_release_of_file_via_close(util):
    # Create a random video file.
    red = ColorClip((256, 200), color=(255, 0, 0))
    green = ColorClip((256, 200), color=(0, 255, 0))
    blue = ColorClip((256, 200), color=(0, 0, 255))

    red.fps = green.fps = blue.fps = 10

    # Repeat this so we can see no conflicts.
    for i in range(3):
        # Get the name of a temporary file we can use.
        local_video_filename = os.path.join(
            util.TMP_DIR, "test_release_of_file_via_close_%s.mp4" % int(time.time())
        )

        clip = clips_array([[red, green, blue]]).with_duration(0.5)
        clip.write_videofile(local_video_filename)

        # Open it up with VideoFileClip.
        video = VideoFileClip(local_video_filename)
        video.close()
        clip.close()

        # Now remove the temporary file.
        # This would fail on Windows if the file is still locked.

        # This should succeed without exceptions.
        os.remove(local_video_filename)

    red.close()
    green.close()
    blue.close()


def test_failure_to_release_file(util):
    """Expected to fail. It demonstrates that there *is* a problem with not
    releasing resources when running on Windows.

    The real issue was that, as of movepy 0.2.3.2, there was no way around it.

    See test_resourcerelease.py to see how the close() methods provide a solution.
    """
    # Get the name of a temporary file we can use.
    local_video_filename = os.path.join(
        util.TMP_DIR, "test_release_of_file_%s.mp4" % int(time.time())
    )

    # Repeat this so we can see that the problems escalate:
    for i in range(5):
        # Create a random video file.
        red = ColorClip((256, 200), color=(255, 0, 0))
        green = ColorClip((256, 200), color=(0, 255, 0))
        blue = ColorClip((256, 200), color=(0, 0, 255))

        red.fps = green.fps = blue.fps = 30
        video = clips_array([[red, green, blue]]).with_duration(1)

        try:
            video.write_videofile(local_video_filename)

            # Open it up with VideoFileClip.
            clip = VideoFileClip(local_video_filename)

            # Normally a client would do processing here.

            # All finished, so delete the clipS.
            clip.close()
            video.close()
            del clip
            del video

        except IOError:
            print(
                "On Windows, this succeeds the first few times around the loop"
                " but eventually fails."
            )
            print("Need to shut down the process now. No more tests in this file.")
            return

        try:
            # Now remove the temporary file.
            # This will fail on Windows if the file is still locked.

            # In particular, this raises an exception with PermissionError.
            # In  there was no way to avoid it.

            os.remove(local_video_filename)
            print("You are not running Windows, because that worked.")
        except OSError:  # More specifically, PermissionError in Python 3.
            print("Yes, on Windows this fails.")


def test_read_transparent_video():
    reader = FFMPEG_VideoReader("media/transparent.webm", pixel_format="rgba")

    # Get first frame
    frame = reader.get_frame(0)
    mask = frame[:, :, 3]

    # Check transparency on fully transparent part is 0
    assert mask[10, 10] == 0

    # Check transparency on fully opaque part is 255
    assert mask[100, 100] == 255


if __name__ == "__main__":
    pytest.main()
