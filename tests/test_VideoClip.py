import os

import pytest
from numpy import pi, sin, array

from moviepy.audio.AudioClip import AudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.utils import close_all_clips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.speedx import speedx
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ColorClip, BitmapClip

from tests.test_helper import TMP_DIR


def test_aspect_ratio():
    clip = BitmapClip([["AAA", "BBB"]], fps=1)
    assert clip.aspect_ratio == 1.5


def test_check_codec():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm")
    location = os.path.join(TMP_DIR, "not_a_video.mas")
    try:
        clip.write_videofile(location)
    except ValueError as e:
        assert (
            "MoviePy couldn't find the codec associated with the filename."
            " Provide the 'codec' parameter in write_videofile." in str(e)
        )
    close_all_clips(locals())


def test_write_frame_errors():
    """Checks error cases return helpful messages"""
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm")
    location = os.path.join(TMP_DIR, "unlogged-write.mp4")
    with pytest.raises(IOError) as e:
        clip.write_videofile(location, codec="nonexistent-codec")
    assert (
        "The video export failed because FFMPEG didn't find the specified codec for video "
        "encoding nonexistent-codec" in str(e.value)
    ), e.value
    close_all_clips(locals())


def test_write_frame_errors_with_redirected_logs():
    """Checks error cases return helpful messages even when logs redirected
    See https://github.com/Zulko/moviepy/issues/877"""
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm")
    location = os.path.join(TMP_DIR, "logged-write.mp4")
    with pytest.raises(IOError) as e:
        clip.write_videofile(location, codec="nonexistent-codec", write_logfile=True)
    assert (
        "The video export failed because FFMPEG didn't find the specified codec for video "
        "encoding nonexistent-codec" in str(e.value)
    )
    close_all_clips(locals())


def test_write_videofiles_with_temp_audiofile_path():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.5)
    location = os.path.join(TMP_DIR, "temp_audiofile_path.webm")
    temp_location = "temp_audiofile"
    if not os.path.exists(temp_location):
        os.mkdir(temp_location)
    clip.write_videofile(location, temp_audiofile_path=temp_location, remove_temp=False)
    assert os.path.isfile(location)
    contents_of_temp_dir = os.listdir(temp_location)
    assert any(file.startswith("temp_audiofile_path") for file in contents_of_temp_dir)


def test_save_frame():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm")
    location = os.path.join(TMP_DIR, "save_frame.png")
    clip.save_frame(location, t=0.5)
    assert os.path.isfile(location)
    close_all_clips(locals())


def test_write_image_sequence():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.24)
    locations = clip.write_images_sequence(os.path.join(TMP_DIR, "frame%02d.png"))
    for location in locations:
        assert os.path.isfile(location)
    close_all_clips(locals())


def test_write_gif_imageio():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.8)
    location = os.path.join(TMP_DIR, "imageio_gif.gif")
    clip.write_gif(location, program="imageio")
    assert os.path.isfile(location)
    close_all_clips(locals())


def test_write_gif_ffmpeg():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.4)
    location = os.path.join(TMP_DIR, "ffmpeg_gif.gif")
    clip.write_gif(location, program="ffmpeg")
    assert os.path.isfile(location)
    close_all_clips(locals())


def test_write_gif_ffmpeg_pixel_format():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.4)
    location = os.path.join(TMP_DIR, "ffmpeg_gif.gif")
    clip.write_gif(location, program="ffmpeg", pixel_format="bgr24")
    assert os.path.isfile(location)
    close_all_clips(locals())


def test_write_gif_ffmpeg_tmpfiles():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.24)
    location = os.path.join(TMP_DIR, "ffmpeg_tmpfiles_gif.gif")
    clip.write_gif(location, program="ffmpeg", tempfiles=True)
    assert os.path.isfile(location)
    close_all_clips(locals())


def test_write_gif_ffmpeg_tmpfiles_pixel_format():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.24)
    location = os.path.join(TMP_DIR, "ffmpeg_tmpfiles_gif.gif")
    clip.write_gif(location, program="ffmpeg", tempfiles=True, pixel_format="bgr24")
    assert os.path.isfile(location)
    close_all_clips(locals())


def test_write_gif_ImageMagick():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.5)
    location = os.path.join(TMP_DIR, "imagemagick_gif.gif")
    clip.write_gif(location, program="ImageMagick")
    close_all_clips(locals())
    # Fails for some reason
    # assert os.path.isfile(location)


def test_write_gif_ImageMagick_tmpfiles():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.24)
    location = os.path.join(TMP_DIR, "imagemagick_tmpfiles_gif.gif")
    clip.write_gif(location, program="ImageMagick", tempfiles=True)
    assert os.path.isfile(location)
    close_all_clips(locals())


def test_write_gif_ImageMagick_tmpfiles_pixel_format():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.24)
    location = os.path.join(TMP_DIR, "imagemagick_tmpfiles_gif.gif")
    clip.write_gif(location, program="ImageMagick", tempfiles=True, pixel_format="SGI")
    assert os.path.isfile(location)
    close_all_clips(locals())


def test_subfx():
    clip = VideoFileClip("media/big_buck_bunny_0_30.webm").subclip(0, 1)
    transform = lambda c: speedx(c, 0.5)
    new_clip = clip.subfx(transform, 0.5, 0.8)
    location = os.path.join(TMP_DIR, "subfx.mp4")
    new_clip.write_videofile(location)
    assert os.path.isfile(location)
    close_all_clips(locals())


def test_oncolor():
    # It doesn't need to be a ColorClip
    clip = ColorClip(size=(100, 60), color=(255, 0, 0), duration=0.5)
    on_color_clip = clip.on_color(size=(200, 160), color=(0, 0, 255))
    location = os.path.join(TMP_DIR, "oncolor.mp4")
    on_color_clip.write_videofile(location, fps=24)
    assert os.path.isfile(location)

    # test constructor with default arguements
    clip = ColorClip(size=(100, 60), is_mask=True)
    clip = ColorClip(size=(100, 60), is_mask=False)

    # negative test
    with pytest.raises(Exception):
        clip = ColorClip(size=(100, 60), color=(255, 0, 0), is_mask=True)

    with pytest.raises(Exception):
        clip = ColorClip(size=(100, 60), color=0.4, is_mask=False)

    close_all_clips(locals())


def test_setaudio():
    clip = ColorClip(size=(100, 60), color=(255, 0, 0), duration=0.5)
    make_frame_440 = lambda t: [sin(440 * 2 * pi * t)]
    audio = AudioClip(make_frame_440, duration=0.5)
    audio.fps = 44100
    clip = clip.with_audio(audio)
    location = os.path.join(TMP_DIR, "setaudio.mp4")
    clip.write_videofile(location, fps=24)
    assert os.path.isfile(location)
    close_all_clips(locals())


def test_setaudio_with_audiofile():
    clip = ColorClip(size=(100, 60), color=(255, 0, 0), duration=0.5)
    audio = AudioFileClip("media/crunching.mp3").subclip(0, 0.5)
    clip = clip.with_audio(audio)
    location = os.path.join(TMP_DIR, "setaudiofile.mp4")
    clip.write_videofile(location, fps=24)
    assert os.path.isfile(location)
    close_all_clips(locals())


def test_setopacity():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.6)
    clip = clip.with_opacity(0.5)
    clip = clip.on_color(size=(1000, 1000), color=(0, 0, 255), col_opacity=0.8)
    location = os.path.join(TMP_DIR, "setopacity.mp4")
    clip.write_videofile(location)
    assert os.path.isfile(location)
    close_all_clips(locals())


def test_with_layer():
    bottom_clip = BitmapClip([["ABC"], ["BCA"], ["CAB"]], fps=1).with_layer(1)
    top_clip = BitmapClip([["DEF"], ["EFD"]], fps=1).with_layer(2)

    composite_clip = CompositeVideoClip([bottom_clip, top_clip])
    reversed_composite_clip = CompositeVideoClip([top_clip, bottom_clip])

    # Make sure that the order of clips makes no difference to the composite clip
    assert composite_clip.subclip(0, 2) == reversed_composite_clip.subclip(0, 2)

    # Make sure that only the 'top' clip is kept
    assert top_clip.subclip(0, 2) == composite_clip.subclip(0, 2)

    # Make sure that it works even when there is only one clip playing at that time
    target_clip = BitmapClip([["DEF"], ["EFD"], ["CAB"]], fps=1)
    assert composite_clip == target_clip


def test_compositing_with_same_layers():
    bottom_clip = BitmapClip([["ABC"], ["BCA"]], fps=1)
    top_clip = BitmapClip([["DEF"], ["EFD"]], fps=1)

    composite_clip = CompositeVideoClip([bottom_clip, top_clip])
    reversed_composite_clip = CompositeVideoClip([top_clip, bottom_clip])

    assert composite_clip == top_clip
    assert reversed_composite_clip == bottom_clip


def test_toimageclip():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.6)
    clip = clip.to_ImageClip(t=0.1, duration=0.4)
    location = os.path.join(TMP_DIR, "toimageclip.mp4")
    clip.write_videofile(location, fps=24)
    assert os.path.isfile(location)
    close_all_clips(locals())


def test_withoutaudio():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.6)
    new_clip = clip.without_audio()
    assert new_clip.audio is None
    close_all_clips(locals())


def test_setfps_withoutchangeduration():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0, 1)
    # The sum is unique for each frame, so we can use it as a frame-ID
    # to check which frames are being preserved
    clip_sums = [f.sum() for f in clip.iter_frames()]

    clip2 = clip.with_fps(48)
    clip2_sums = [f.sum() for f in clip2.iter_frames()]
    assert clip2_sums[::2] == clip_sums
    assert clip2.duration == clip.duration
    close_all_clips(locals())


def test_setfps_withchangeduration():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0, 1)
    # The sum is unique for each frame, so we can use it as a frame-ID
    # to check which frames are being preserved
    clip_sums = [f.sum() for f in clip.iter_frames()]

    clip2 = clip.with_fps(48, change_duration=True)
    clip2_sums = [f.sum() for f in clip2.iter_frames()]
    assert clip2_sums == clip_sums
    assert clip2.duration == clip.duration / 2
    close_all_clips(locals())


if __name__ == "__main__":
    pytest.main()
