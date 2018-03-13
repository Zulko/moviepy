import sys
import os
from numpy import sin, pi

import pytest

from moviepy.video.VideoClip import VideoClip, ColorClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.AudioClip import AudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.fx.speedx import speedx

sys.path.append("tests")
import download_media
from test_helper import TMP_DIR


def test_download_media(capsys):
    with capsys.disabled():
        download_media.download()


def test_check_codec():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm")
    location = os.path.join(TMP_DIR, "not_a_video.mas")
    try:
        clip.write_videofile(location)
    except ValueError as e:
        assert "MoviePy couldn't find the codec associated with the filename." \
               " Provide the 'codec' parameter in write_videofile." in str(e)


def test_save_frame():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm")
    location = os.path.join(TMP_DIR, "save_frame.png")
    clip.save_frame(location, t=0.5)
    assert os.path.isfile(location)


def test_write_image_sequence():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.3)
    locations = clip.write_images_sequence(os.path.join(TMP_DIR, "frame%02d.png"))
    for location in locations:
        assert os.path.isfile(location)


def test_write_gif_imageio():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.8)
    location = os.path.join(TMP_DIR, "imageio_gif.gif")
    clip.write_gif(location, program="imageio")
    assert os.path.isfile(location)


def test_write_gif_ffmpeg():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm")
    location = os.path.join(TMP_DIR, "ffmpeg_gif.gif")
    clip.write_gif(location, program="ffmpeg")
    assert os.path.isfile(location)


def test_write_gif_ffmpeg_tmpfiles():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.4)
    location = os.path.join(TMP_DIR, "ffmpeg_tmpfiles_gif.gif")
    clip.write_gif(location, program="ffmpeg", tempfiles=True)
    assert os.path.isfile(location)


def test_write_gif_ImageMagick():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm")
    location = os.path.join(TMP_DIR, "imagemagick_gif.gif")
    clip.write_gif(location, program="ImageMagick")
    # Fails for some reason
    #assert os.path.isfile(location)


def test_write_gif_ImageMagick_tmpfiles():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.5)
    location = os.path.join(TMP_DIR, "imagemagick_tmpfiles_gif.gif")
    clip.write_gif(location, program="ImageMagick", tempfiles=True)
    assert os.path.isfile(location)


def test_subfx():
    clip = VideoFileClip("media/big_buck_bunny_0_30.webm").subclip(0, 5)
    transform = lambda c: speedx(c, 0.5)
    new_clip = clip.subfx(transform, 2, 4)
    location = os.path.join(TMP_DIR, "subfx.mp4")
    new_clip.write_videofile(location)
    assert os.path.isfile(location)


def test_oncolor():
    # It doesn't need to be a ColorClip
    clip = ColorClip(size=(100, 60), color=(255, 0, 0), duration=4)
    on_color_clip = clip.on_color(size=(200, 160), color=(0, 0, 255))
    location = os.path.join(TMP_DIR, "oncolor.mp4")
    on_color_clip.write_videofile(location, fps=24)
    assert os.path.isfile(location)


def test_setaudio():
    clip = ColorClip(size=(100, 60), color=(255, 0, 0), duration=2)
    make_frame_440 = lambda t: [sin(440 * 2 * pi * t)]
    audio = AudioClip(make_frame_440, duration=2)
    audio.fps = 44100
    clip = clip.set_audio(audio)
    location = os.path.join(TMP_DIR, "setaudio.mp4")
    clip.write_videofile(location, fps=24)
    assert os.path.isfile(location)


def test_setaudio_with_audiofile():
    clip = ColorClip(size=(100, 60), color=(255, 0, 0), duration=2)
    audio = AudioFileClip("media/crunching.mp3").subclip(0, 2)
    clip = clip.set_audio(audio)
    location = os.path.join(TMP_DIR, "setaudiofile.mp4")
    clip.write_videofile(location, fps=24)
    assert os.path.isfile(location)


def test_setopacity():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.6)
    clip = clip.set_opacity(0.5)
    clip = clip.on_color(size=(1000, 1000), color=(0, 0, 255), col_opacity=0.8)
    location = os.path.join(TMP_DIR, "setopacity.mp4")
    clip.write_videofile(location)
    assert os.path.isfile(location)


def test_toimageclip():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.6)
    clip = clip.to_ImageClip(t=0.1, duration=2)
    location = os.path.join(TMP_DIR, "toimageclip.mp4")
    clip.write_videofile(location, fps=24)
    assert os.path.isfile(location)


def test_withoutaudio():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm")
    new_clip = clip.without_audio()
    assert new_clip.audio is None


if __name__ == "__main__":
    pytest.main()
