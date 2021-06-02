"""VideoClip tests."""

import copy
import os

import numpy as np
from PIL import Image

import pytest

from moviepy.audio.AudioClip import AudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.tools import convert_to_seconds
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.mask_color import mask_color
from moviepy.video.fx.multiply_speed import multiply_speed
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import BitmapClip, ColorClip, ImageClip, VideoClip


def test_aspect_ratio():
    clip = BitmapClip([["AAA", "BBB"]], fps=1)
    assert clip.aspect_ratio == 1.5


@pytest.mark.parametrize(
    ("duration", "fps", "expected_n_frames"),
    (
        (1, 60, 60),
        (0.1, 100, 10),
        (2.4, 60, 144),
    ),
)
def test_n_frames(duration, fps, expected_n_frames):
    clip = VideoClip(duration=duration).with_fps(fps)
    assert clip.n_frames == expected_n_frames


def test_with_audio(stereo_wave):
    clip = VideoClip(duration=1).with_fps(1)
    assert clip.audio is None

    audio_clip = AudioClip(stereo_wave(), duration=1, fps=22050)
    assert clip.with_audio(audio_clip).audio is audio_clip


def test_without_audio(stereo_wave):
    audio_clip = AudioClip(stereo_wave(), duration=1, fps=22050)
    clip = VideoClip(duration=1).with_fps(1).with_audio(audio_clip)

    assert clip.audio is audio_clip
    assert clip.without_audio().audio is None


def test_check_codec(util, video):
    clip = video()
    location = os.path.join(util.TMP_DIR, "not_a_video.mas")
    try:
        clip.write_videofile(location)
    except ValueError as e:
        assert (
            "MoviePy couldn't find the codec associated with the filename."
            " Provide the 'codec' parameter in write_videofile." in str(e)
        )


def test_write_frame_errors(util, video):
    """Checks error cases return helpful messages."""
    clip = video()
    location = os.path.join(util.TMP_DIR, "unlogged-write.mp4")
    with pytest.raises(IOError) as e:
        clip.write_videofile(location, codec="nonexistent-codec")
    assert (
        "The video export failed because FFMPEG didn't find the specified"
        " codec for video encoding nonexistent-codec" in str(e.value)
    ), e.value

    autogenerated_location = "unlogged-writeTEMP_MPY_wvf_snd.mp3"
    if os.path.exists(autogenerated_location):
        os.remove(autogenerated_location)


def test_write_frame_errors_with_redirected_logs(util, video):
    """Checks error cases return helpful messages even when logs redirected.
    See https://github.com/Zulko/moviepy/issues/877
    """
    clip = video()
    location = os.path.join(util.TMP_DIR, "logged-write.mp4")
    with pytest.raises(IOError) as e:
        clip.write_videofile(location, codec="nonexistent-codec", write_logfile=True)
    assert (
        "The video export failed because FFMPEG didn't find the specified"
        " codec for video encoding nonexistent-codec" in str(e.value)
    )

    autogenerated_location_mp3 = "logged-writeTEMP_MPY_wvf_snd.mp3"
    autogenerated_location_log = autogenerated_location_mp3 + ".log"
    for fp in [autogenerated_location_mp3, autogenerated_location_log]:
        if os.path.exists(fp):
            os.remove(fp)


def test_write_videofiles_with_temp_audiofile_path(util):
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0.2, 0.5)
    location = os.path.join(util.TMP_DIR, "temp_audiofile_path.webm")
    temp_location = os.path.join(util.TMP_DIR, "temp_audiofile")
    if not os.path.exists(temp_location):
        os.mkdir(temp_location)
    clip.write_videofile(location, temp_audiofile_path=temp_location, remove_temp=False)
    assert os.path.isfile(location)
    contents_of_temp_dir = os.listdir(temp_location)
    assert any(file.startswith("temp_audiofile_path") for file in contents_of_temp_dir)


@pytest.mark.parametrize("mask_color", (0, 0.5, 0.8, 1))
@pytest.mark.parametrize(
    "with_mask",
    (False, True),
    ids=("mask", ""),
)
@pytest.mark.parametrize("t", (0, "00:00:01", (0, 0, 2)), ids=("t=0", "t=1", "t=2"))
@pytest.mark.parametrize(
    "frames",
    (
        pytest.param(
            [["RR", "RR"], ["GG", "GG"], ["BB", "BB"]],
            id="RGB 2x2",
        ),
        pytest.param(
            [["O", "O"], ["W", "W"], ["B", "B"]],
            id="OWB 2x1",
        ),
    ),
)
def test_save_frame(util, with_mask, t, mask_color, frames):
    filename = os.path.join(util.TMP_DIR, "moviepy_VideoClip_save_frame.png")
    if os.path.isfile(filename):
        os.remove(filename)

    width, height = (len(frames[0][0]), len(frames[0]))

    clip = BitmapClip(frames, fps=1)
    if with_mask:
        mask = ColorClip(color=mask_color, is_mask=True, size=(width, height))
        clip = clip.with_mask(mask)

    clip.save_frame(filename, t)

    t = int(convert_to_seconds(t))

    # expected RGB
    e_r, e_g, e_b = BitmapClip.DEFAULT_COLOR_DICT[frames[t][0][0]]

    im = Image.open(filename, mode="r")
    assert im.width == width
    assert im.height == height

    for i in range(im.width):
        for j in range(im.height):
            rgba = im.getpixel((i, j))
            if len(rgba) == 4:
                r, g, b, a = rgba
            else:
                r, g, b = rgba

            assert r == e_r
            assert g == e_g
            assert b == e_b

            if with_mask:
                assert round(a / 254, 2) == mask_color


def test_write_image_sequence(util, video):
    clip = video(start_time=0.2, end_time=0.24)
    locations = clip.write_images_sequence(os.path.join(util.TMP_DIR, "frame%02d.png"))
    for location in locations:
        assert os.path.isfile(location)


def test_write_gif_imageio(util, video):
    clip = video(start_time=0.2, end_time=0.8)
    location = os.path.join(util.TMP_DIR, "imageio_gif.gif")
    clip.write_gif(location, program="imageio")
    assert os.path.isfile(location)


def test_write_gif_ffmpeg(util, video):
    clip = video(start_time=0.2, end_time=0.28)
    location = os.path.join(util.TMP_DIR, "ffmpeg_gif.gif")
    clip.write_gif(location, program="ffmpeg")
    assert os.path.isfile(location)


def test_write_gif_ffmpeg_pixel_format(util, video):
    clip = video(start_time=0.2, end_time=0.28)
    location = os.path.join(util.TMP_DIR, "ffmpeg_gif.gif")
    clip.write_gif(location, program="ffmpeg", pixel_format="bgr24")
    assert os.path.isfile(location)


def test_write_gif_ffmpeg_tmpfiles(util, video):
    clip = video(start_time=0.2, end_time=0.24)
    location = os.path.join(util.TMP_DIR, "ffmpeg_tmpfiles_gif.gif")
    clip.write_gif(location, program="ffmpeg", tempfiles=True)
    assert os.path.isfile(location)


def test_write_gif_ffmpeg_tmpfiles_pixel_format(util, video):
    clip = video(start_time=0.2, end_time=0.24)
    location = os.path.join(util.TMP_DIR, "ffmpeg_tmpfiles_gif.gif")
    clip.write_gif(location, program="ffmpeg", tempfiles=True, pixel_format="bgr24")
    assert os.path.isfile(location)


def test_write_gif_ImageMagick(util, video):
    clip = video(start_time=0.2, end_time=0.5)
    location = os.path.join(util.TMP_DIR, "imagemagick_gif.gif")
    clip.write_gif(location, program="ImageMagick")
    # Fails for some reason
    # assert os.path.isfile(location)


def test_write_gif_ImageMagick_tmpfiles(util, video):
    clip = video(start_time=0.2, end_time=0.24)
    location = os.path.join(util.TMP_DIR, "imagemagick_tmpfiles_gif.gif")
    clip.write_gif(location, program="ImageMagick", tempfiles=True)
    assert os.path.isfile(location)


def test_write_gif_ImageMagick_tmpfiles_pixel_format(util, video):
    clip = video(start_time=0.2, end_time=0.24)
    location = os.path.join(util.TMP_DIR, "imagemagick_tmpfiles_gif.gif")
    clip.write_gif(location, program="ImageMagick", tempfiles=True, pixel_format="SGI")
    assert os.path.isfile(location)


def test_subfx(util):
    clip = VideoFileClip("media/big_buck_bunny_0_30.webm").subclip(0, 1)
    transform = lambda c: multiply_speed(c, 0.5)
    new_clip = clip.subfx(transform, 0.5, 0.8)
    location = os.path.join(util.TMP_DIR, "subfx.mp4")
    new_clip.write_videofile(location)
    assert os.path.isfile(location)


def test_oncolor(util):
    # It doesn't need to be a ColorClip
    clip = ColorClip(size=(100, 60), color=(255, 0, 0), duration=0.5)
    on_color_clip = clip.on_color(size=(200, 160), color=(0, 0, 255))
    location = os.path.join(util.TMP_DIR, "oncolor.mp4")
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


def test_setaudio(util):
    clip = ColorClip(size=(100, 60), color=(255, 0, 0), duration=0.5)
    make_frame_440 = lambda t: [np.sin(440 * 2 * np.pi * t)]
    audio = AudioClip(make_frame_440, duration=0.5)
    audio.fps = 44100
    clip = clip.with_audio(audio)
    location = os.path.join(util.TMP_DIR, "setaudio.mp4")
    clip.write_videofile(location, fps=24)
    assert os.path.isfile(location)


def test_setaudio_with_audiofile(util):
    clip = ColorClip(size=(100, 60), color=(255, 0, 0), duration=0.5)
    audio = AudioFileClip("media/crunching.mp3").subclip(0, 0.5)
    clip = clip.with_audio(audio)
    location = os.path.join(util.TMP_DIR, "setaudiofile.mp4")
    clip.write_videofile(location, fps=24)
    assert os.path.isfile(location)


def test_setopacity(util, video):
    clip = video(start_time=0.2, end_time=0.6)
    clip = clip.with_opacity(0.5)
    clip = clip.on_color(size=(1000, 1000), color=(0, 0, 255), col_opacity=0.8)
    location = os.path.join(util.TMP_DIR, "setopacity.mp4")
    clip.write_videofile(location)
    assert os.path.isfile(location)


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


def test_toimageclip(util, video):
    clip = video(start_time=0.2, end_time=0.6)
    clip = clip.to_ImageClip(t=0.1, duration=0.4)
    location = os.path.join(util.TMP_DIR, "toimageclip.mp4")
    clip.write_videofile(location, fps=24)
    assert os.path.isfile(location)


def test_withoutaudio(video):
    clip = video(start_time=0.2, end_time=0.6)
    new_clip = clip.without_audio()
    assert new_clip.audio is None


def test_setfps_withoutchangeduration(video):
    clip = video()
    # The sum is unique for each frame, so we can use it as a frame-ID
    # to check which frames are being preserved
    clip_sums = [f.sum() for f in clip.iter_frames()]

    clip2 = clip.with_fps(48)
    clip2_sums = [f.sum() for f in clip2.iter_frames()]
    assert clip2_sums[::2] == clip_sums
    assert clip2.duration == clip.duration


def test_setfps_withchangeduration(video):
    clip = video(end_time=0.2)
    # The sum is unique for each frame, so we can use it as a frame-ID
    # to check which frames are being preserved
    clip_sums = [f.sum() for f in clip.iter_frames()]

    clip2 = clip.with_fps(48, change_duration=True)
    clip2_sums = [f.sum() for f in clip2.iter_frames()]
    assert clip2_sums == clip_sums
    assert clip2.duration == clip.duration / 2


def test_copied_videoclip_write_videofile(util):
    """Check if a copied ``VideoClip`` instance can render a file which has
    the same features as the copied clip when opening with ``VideoFileClip``.
    """
    clip = BitmapClip([["RRR", "GGG", "BBB"]], fps=1)
    copied_clip = clip.copy()

    output_filepath = os.path.join(util.TMP_DIR, "copied_videoclip_from_bitmap.webm")
    copied_clip.write_videofile(output_filepath)
    copied_clip_from_file = VideoFileClip(output_filepath)

    assert list(copied_clip.size) == copied_clip_from_file.size
    assert copied_clip.duration == copied_clip_from_file.duration


@pytest.mark.parametrize(
    "copy_func",
    (
        lambda clip: clip.copy(),
        lambda clip: copy.copy(clip),
        lambda clip: copy.deepcopy(clip),
    ),
    ids=("clip.copy()", "copy.copy(clip)", "copy.deepcopy(clip)"),
)
def test_videoclip_copy(copy_func):
    """It must be possible to do a mixed copy of VideoClip using ``clip.copy()``,
    ``copy.copy(clip)`` and ``copy.deepcopy(clip)``.
    """
    clip = VideoClip()
    other_clip = VideoClip()

    for attr in clip.__dict__:
        # mask and audio are shallow copies that should be initialized
        if attr in ("mask", "audio"):
            if attr == "mask":
                nested_object = BitmapClip([["R"]], duration=0.01)
            else:
                nested_object = AudioClip(
                    lambda t: [np.sin(880 * 2 * np.pi * t)], duration=0.01, fps=44100
                )
            setattr(clip, attr, nested_object)
        else:
            setattr(clip, attr, "foo")

    copied_clip = copy_func(clip)

    # VideoClip attributes are copied
    for attr in copied_clip.__dict__:
        value = getattr(copied_clip, attr)
        assert value == getattr(clip, attr)

        # other instances are not edited
        assert value != getattr(other_clip, attr)

        # shallow copies of mask and audio
        if attr in ("mask", "audio"):
            for nested_attr in value.__dict__:
                assert getattr(value, nested_attr) == getattr(
                    getattr(clip, attr), nested_attr
                )

    # nested objects of instances copies are not edited
    assert other_clip.mask is None
    assert other_clip.audio is None


def test_afterimage(util):
    ai = ImageClip("media/afterimage.png")
    masked_clip = mask_color(ai, color=[0, 255, 1])  # for green
    some_background_clip = ColorClip((800, 600), color=(255, 255, 255))
    final_clip = CompositeVideoClip(
        [some_background_clip, masked_clip], use_bgclip=True
    ).with_duration(0.2)

    filename = os.path.join(util.TMP_DIR, "afterimage.mp4")
    final_clip.write_videofile(filename, fps=30, logger=None)


if __name__ == "__main__":
    pytest.main()
