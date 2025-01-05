"""Issue tests meant to be run with pytest."""

import os

import numpy as np

import pytest

from moviepy import *


try:
    import matplotlib.pyplot
except ImportError:
    matplotlib = None
else:
    matplotlib = True


def test_issue_145():
    video = ColorClip((800, 600), color=(255, 0, 0)).with_duration(5)
    with pytest.raises(Exception):
        concatenate_videoclips([video], method="composite")


def test_issue_190():
    # from PIL import Image
    #
    # filename = os.path.join(util.TMP_DIR, "issue_190.png")
    # Image.new('L', (800,600), 'white').save(filename)
    #
    # from imageio import imread
    # image = imread(filename)
    #
    # clip = ImageSequenceClip([image, image], fps=1)
    # clip.write_videofile(os.path.splitext(filename)[0] + ".mp4"))
    pass


def test_issue_285():
    clip_1, clip_2, clip_3 = (
        ImageClip("media/python_logo.png", duration=10),
        ImageClip("media/python_logo.png", duration=10),
        ImageClip("media/python_logo.png", duration=10),
    )
    merged_clip = concatenate_videoclips([clip_1, clip_2, clip_3])
    assert merged_clip.duration == 30


def test_issue_334(util):
    # NOTE: this is horrible. Any simpler version ?
    last_move = None
    last_move1 = None

    lis = [
        (0.0, 113, 167, 47),
        (0.32, 138, 159, 47),
        (0.44, 152, 144, 47),
        (0.48, 193, 148, 47),
        (0.6, 193, 148, 47),
        (0.76, 205, 138, 55),
        (0.88, 204, 121, 63),
        (0.92, 190, 31, 127),
        (1.2, 183, 59, 127),
        (1.4, 137, 22, 127),
        (1.52, 137, 22, 127),
        (1.72, 129, 67, 127),
        (1.88, 123, 69, 127),
        (2.04, 131, 123, 63),
        (2.24, 130, 148, 63),
        (2.48, 130, 148, 63),
        (2.8, 138, 180, 63),
        (3.0, 138, 180, 63),
        (3.2, 146, 192, 63),
        (3.28, 105, 91, 151),
        (3.44, 105, 91, 151),
        (3.72, 11, 48, 151),
        (3.96, 5, 78, 151),
        (4.32, 4, 134, 1),
        (4.6, 149, 184, 48),
        (4.8, 145, 188, 48),
        (5.0, 154, 217, 48),
        (5.08, 163, 199, 48),
        (5.2, 163, 199, 48),
        (5.32, 164, 187, 48),
        (5.48, 163, 200, 48),
        (5.76, 163, 200, 48),
        (5.96, 173, 199, 48),
        (6.0, 133, 172, 48),
        (6.04, 128, 165, 48),
        (6.28, 128, 165, 48),
        (6.4, 129, 180, 48),
        (6.52, 133, 166, 48),
        (6.64, 133, 166, 48),
        (6.88, 144, 183, 48),
        (7.0, 153, 174, 48),
        (7.16, 153, 174, 48),
        (7.24, 153, 174, 48),
        (7.28, 253, 65, 104),
        (7.64, 253, 65, 104),
        (7.8, 279, 116, 80),
        (8.0, 290, 105, 80),
        (8.24, 288, 124, 80),
        (8.44, 243, 102, 80),
        (8.56, 243, 102, 80),
        (8.8, 202, 107, 80),
        (8.84, 164, 27, 104),
        (9.0, 164, 27, 104),
        (9.12, 121, 9, 104),
        (9.28, 77, 33, 104),
        (9.32, 52, 23, 104),
        (9.48, 52, 23, 104),
        (9.64, 33, 46, 104),
        (9.8, 93, 49, 104),
        (9.92, 93, 49, 104),
        (10.16, 173, 19, 104),
        (10.2, 226, 173, 48),
        (10.36, 226, 173, 48),
        (10.48, 211, 172, 48),
        (10.64, 208, 162, 48),
        (10.92, 220, 171, 48),
    ]

    lis1 = [
        (0.0, 113, 167, 47),
        (0.32, 138, 159, 47),
        (0.44, 152, 144, 47),
        (0.48, 193, 148, 47),
        (0.6, 193, 148, 47),
        (0.76, 205, 138, 55),
        (0.88, 204, 121, 63),
        (0.92, 190, 31, 127),
        (1.2, 183, 59, 127),
        (1.4, 137, 22, 127),
        (1.52, 137, 22, 127),
        (1.72, 129, 67, 127),
        (1.88, 123, 69, 127),
        (2.04, 131, 123, 63),
        (2.24, 130, 148, 63),
        (2.48, 130, 148, 63),
        (2.8, 138, 180, 63),
        (3.0, 138, 180, 63),
        (3.2, 146, 192, 63),
        (3.28, 105, 91, 151),
        (3.44, 105, 91, 151),
        (3.72, 11, 48, 151),
        (3.96, 5, 78, 151),
        (4.32, 4, 134, 1),
        (4.6, 149, 184, 48),
        (4.8, 145, 188, 48),
        (5.0, 154, 217, 48),
        (5.08, 163, 199, 48),
        (5.2, 163, 199, 48),
        (5.32, 164, 187, 48),
        (5.48, 163, 200, 48),
        (5.76, 163, 200, 48),
        (5.96, 173, 199, 48),
        (6.0, 133, 172, 48),
        (6.04, 128, 165, 48),
        (6.28, 128, 165, 48),
        (6.4, 129, 180, 48),
        (6.52, 133, 166, 48),
        (6.64, 133, 166, 48),
        (6.88, 144, 183, 48),
        (7.0, 153, 174, 48),
        (7.16, 153, 174, 48),
        (7.24, 153, 174, 48),
        (7.28, 253, 65, 104),
        (7.64, 253, 65, 104),
        (7.8, 279, 116, 80),
        (8.0, 290, 105, 80),
        (8.24, 288, 124, 80),
        (8.44, 243, 102, 80),
        (8.56, 243, 102, 80),
        (8.8, 202, 107, 80),
        (8.84, 164, 27, 104),
        (9.0, 164, 27, 104),
        (9.12, 121, 9, 104),
        (9.28, 77, 33, 104),
        (9.32, 52, 23, 104),
        (9.48, 52, 23, 104),
        (9.64, 33, 46, 104),
        (9.8, 93, 49, 104),
        (9.92, 93, 49, 104),
        (10.16, 173, 19, 104),
        (10.2, 226, 173, 48),
        (10.36, 226, 173, 48),
        (10.48, 211, 172, 48),
        (10.64, 208, 162, 48),
        (10.92, 220, 171, 48),
    ]

    def posi(t):
        global last_move
        if len(lis) == 0:
            return (last_move[1], last_move[2])
        if t >= lis[0][0]:
            last_move = item = lis.pop(0)
            return (item[1], item[2])
        else:
            if len(lis) > 0:
                dura = lis[0][0] - last_move[0]
                now = t - last_move[0]
                w = (lis[0][1] - last_move[1]) * (now / dura)
                h = (lis[0][2] - last_move[2]) * (now / dura)
                return (last_move[1] + w, last_move[2] + h)
            return (last_move[1], last_move[2])

    def size(t):
        global last_move1
        if len(lis1) == 0:
            return (last_move1[3], last_move1[3] * 1.33)
        if t >= lis1[0][0]:
            last_move1 = item = lis1.pop(0)
            return (item[3], item[3] * 1.33)
        else:
            if len(lis) > 0:
                dura = lis1[0][0] - last_move1[0]
                now = t - last_move1[0]
                s = (lis1[0][3] - last_move1[3]) * (now / dura)
                nsw = last_move1[3] + s
                nsh = nsw * 1.33
                return (nsw, nsh)
            return (last_move1[3], last_move1[3] * 1.33)

    avatar = VideoFileClip("media/big_buck_bunny_432_433.webm", has_mask=True)
    avatar.audio = None
    maskclip = ImageClip("media/afterimage.png", is_mask=True, transparent=True)
    avatar.with_mask(maskclip)  # must set maskclip here..
    concatenated = avatar * 3

    tt = VideoFileClip("media/big_buck_bunny_0_30.webm").subclipped(0, 3)
    # TODO: Setting mask here does not work:
    # .with_mask(maskclip).resize(size)])
    final = CompositeVideoClip(
        [tt, concatenated.with_position(posi).with_effects([vfx.Resize(size)])]
    )
    final.duration = tt.duration
    final.write_videofile(os.path.join(util.TMP_DIR, "issue_334.mp4"), fps=10)


def test_issue_354():
    with ImageClip("media/python_logo.png") as clip:
        clip.duration = 10
        crosstime = 1

        fadecaption = clip.with_effects(
            [vfx.CrossFadeIn(crosstime), vfx.CrossFadeOut(crosstime)]
        )
        CompositeVideoClip([clip, fadecaption]).close()


def test_issue_359(util):
    with ColorClip((800, 600), color=(255, 0, 0)).with_duration(0.2) as video:
        video.fps = 30
        video.write_gif(filename=os.path.join(util.TMP_DIR, "issue_359.gif"))


def test_issue_407():
    red = ColorClip((800, 600), color=(255, 0, 0)).with_duration(5)
    red.fps = 30

    assert red.fps == 30
    assert red.w == 800
    assert red.h == 600
    assert red.size == (800, 600)

    # ColorClip has no fps attribute.
    green = ColorClip((640, 480), color=(0, 255, 0)).with_duration(2)
    blue = ColorClip((640, 480), color=(0, 0, 255)).with_duration(2)

    assert green.w == blue.w == 640
    assert green.h == blue.h == 480
    assert green.size == blue.size == (640, 480)

    with pytest.raises(AttributeError):
        green.fps

    with pytest.raises(AttributeError):
        blue.fps

    video = concatenate_videoclips([red, green, blue])
    assert video.fps == red.fps


def test_issue_416():
    # ColorClip has no fps attribute.
    green = ColorClip((640, 480), color=(0, 255, 0)).with_duration(2)
    video1 = concatenate_videoclips([green])
    assert video1.fps is None


def test_issue_417():
    # failed in python2
    cad = "media/python_logo.png"
    myclip = ImageClip(cad).resized(new_size=[1280, 660])
    CompositeVideoClip([myclip], size=(1280, 720))


def test_issue_470(util):
    wav_filename = os.path.join(util.TMP_DIR, "moviepy_issue_470.wav")

    audio_clip = AudioFileClip("media/crunching.mp3")

    # end_time is out of bounds
    subclip = audio_clip.subclipped(start_time=6, end_time=9)

    with pytest.raises(IOError):
        subclip.write_audiofile(wav_filename, write_logfile=True)

    # but this one should work..
    subclip = audio_clip.subclipped(start_time=6, end_time=8)
    subclip.write_audiofile(wav_filename, write_logfile=True)


def test_issue_547():
    red = ColorClip((640, 480), color=(255, 0, 0)).with_duration(1)
    green = ColorClip((640, 480), color=(0, 255, 0)).with_duration(2)
    blue = ColorClip((640, 480), color=(0, 0, 255)).with_duration(3)

    video = concatenate_videoclips([red, green, blue], method="compose")
    assert video.duration == 6
    assert video.mask.duration == 6

    video = concatenate_videoclips([red, green, blue])
    assert video.duration == 6


def test_issue_636():
    with VideoFileClip("media/big_buck_bunny_0_30.webm").subclipped(0, 11) as video:
        with video.subclipped(0, 1) as _:
            pass


def test_issue_655():
    video_file = "media/fire2.mp4"
    for subclip in [(0, 2), (1, 2), (2, 3)]:
        with VideoFileClip(video_file) as v:
            with v.subclipped(1, 2) as _:
                pass
            next(v.subclipped(*subclip).iter_frames())
    assert True


def test_issue_1682(util):
    filename = "media/big_buck_bunny_0_30.webm"
    clip = VideoFileClip(filename)
    clip = clip.with_section_cut_out(1, 9)
    output_video_filepath = os.path.join(
        util.TMP_DIR, "big_buck_bunny_0_30_cutout.webm"
    )
    clip.write_videofile(output_video_filepath)


def test_issue_1682_2(util):
    filename = "media/rain.mp3"
    clip = AudioFileClip(filename)
    clip = clip.with_section_cut_out(10, 17)
    output_audio_filepath = os.path.join(util.TMP_DIR, "rain_cutout.mp3")
    clip.write_audiofile(output_audio_filepath)


def test_issue_2269(util):
    filename = "media/big_buck_bunny_0_30.webm"
    clip = VideoFileClip(filename).subclipped(0, 3)
    color_clip = ColorClip((500, 200), (255, 0, 0, 255)).with_duration(3)
    txt_clip_with_margin = TextClip(
        text="Hello",
        font=util.FONT,
        font_size=72,
        stroke_color="white",
        stroke_width=10,
        margin=(10, 5, 0, 0),
        text_align="center",
    ).with_duration(3)

    comp1 = CompositeVideoClip(
        [color_clip, txt_clip_with_margin.with_position(("center", "center"))]
    )
    comp2 = CompositeVideoClip([clip, comp1.with_position(("center", "center"))])

    # If transparency work as expected, this pixel should be pure red at 2 seconds
    frame = comp2.get_frame(2)
    pixel = frame[334, 625]

    # We add a bit of tolerance (about 1%) to account
    # For possible rounding errors
    assert np.allclose(pixel, [255, 0, 0], rtol=0.01)


def test_issue_2269_2(util):
    clip1 = ColorClip((200, 200), (255, 0, 0)).with_duration(3)
    clip2 = ColorClip((100, 100), (0, 255, 0, 76.5)).with_duration(3)
    clip3 = ColorClip((50, 50), (0, 0, 255, 76.5)).with_duration(3)

    compostite_clip1 = CompositeVideoClip(
        [clip1, clip2.with_position(("center", "center"))]
    )
    compostite_clip2 = CompositeVideoClip(
        [compostite_clip1, clip3.with_position(("center", "center"))]
    )

    # If transparency work as expected the clip should match thoses colors
    frame = compostite_clip2.get_frame(2)
    pixel1 = frame[100, 10]
    pixel2 = frame[100, 60]
    pixel3 = frame[100, 100]

    # We add a bit of tolerance (about 1%) to account
    # For possible rounding errors
    assert np.allclose(pixel1, [255, 0, 0], rtol=0.01)
    assert np.allclose(pixel2, [179, 76, 0], rtol=0.01)
    assert np.allclose(pixel3, [126, 53, 76], rtol=0.01)


def test_issue_2269_3(util):
    # This time all clips have transparency
    clip1 = ColorClip((200, 200), (255, 0, 0, 76.5)).with_duration(3)
    clip2 = ColorClip((100, 100), (0, 255, 0, 76.5)).with_duration(3)
    clip3 = ColorClip((50, 50), (0, 0, 255, 76.5)).with_duration(3)

    compostite_clip1 = CompositeVideoClip(
        [clip1, clip2.with_position(("center", "center"))]
    )
    compostite_clip2 = CompositeVideoClip(
        [compostite_clip1, clip3.with_position(("center", "center"))]
    )

    # If transparency work as expected the clip transparency should be between 0.3 and 0.657
    frame = compostite_clip2.mask.get_frame(2)
    pixel1 = frame[100, 10]
    pixel2 = frame[100, 60]
    pixel3 = frame[100, 100]
    assert pixel1 == 0.3
    assert pixel2 == 0.51
    assert pixel3 == 0.657


def test_issue_2160(util):
    filename = "media/-video-with-dash-.mp4"
    clip = VideoFileClip(filename)
    output_video_filepath = os.path.join(
        util.TMP_DIR, "big_buck_bunny_0_30_cutout.webm"
    )
    clip.write_videofile(output_video_filepath)


if __name__ == "__main__":
    pytest.main()
