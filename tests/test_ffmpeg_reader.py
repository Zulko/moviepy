"""FFmpeg reader tests meant to be run with pytest."""

import pytest
import numpy as np

from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos, FFMPEG_VideoReader


def test_ffmpeg_parse_infos():
    d = ffmpeg_parse_infos("media/big_buck_bunny_432_433.webm")
    assert d["duration"] == 1.0

    d = ffmpeg_parse_infos("media/pigs_in_a_polka.gif")
    assert d["video_size"] == [314, 273]
    assert d["duration"] == 3.0
    assert not d["audio_found"]

    d = ffmpeg_parse_infos("media/video_with_failing_audio.mp4")
    assert d["audio_found"]
    assert d["audio_fps"] == 44100

    d = ffmpeg_parse_infos("media/crunching.mp3")
    assert d["audio_found"]
    assert d["audio_fps"] == 48000

    d = ffmpeg_parse_infos("media/sintel_with_15_chapters.mp4")
    assert d["audio_bitrate"]
    assert d["video_bitrate"]


def test_ffmpeg_parse_infos_duration():
    infos = ffmpeg_parse_infos("media/big_buck_bunny_0_30.webm")
    assert infos["video_nframes"] == 720

    infos = ffmpeg_parse_infos("media/bitmap.mp4")
    assert infos["video_nframes"] == 5


def test_ffmpeg_parse_infos_for_i926():
    d = ffmpeg_parse_infos("media/sintel_with_15_chapters.mp4")
    assert d["audio_found"]


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
