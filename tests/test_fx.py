import os
import sys

import pytest

from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.utils import close_all_clips
from moviepy.video.VideoClip import BitmapClip, ColorClip
from moviepy.video.fx.blackwhite import blackwhite

# from moviepy.video.fx.blink import blink
from moviepy.video.fx.colorx import colorx
from moviepy.video.fx.crop import crop
from moviepy.video.fx.even_size import even_size
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.freeze import freeze
from moviepy.video.fx.invert_colors import invert_colors
from moviepy.video.fx.loop import loop
from moviepy.video.fx.lum_contrast import lum_contrast
from moviepy.video.fx.make_loopable import make_loopable
from moviepy.video.fx.margin import margin
from moviepy.video.fx.mirror_x import mirror_x
from moviepy.video.fx.mirror_y import mirror_y
from moviepy.video.fx.resize import resize
from moviepy.video.fx.rotate import rotate
from moviepy.video.fx.speedx import speedx
from moviepy.video.fx.time_mirror import time_mirror
from moviepy.video.fx.time_symmetrize import time_symmetrize
from moviepy.video.io.VideoFileClip import VideoFileClip

from tests.test_helper import TMP_DIR


def get_test_video():
    return VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0, 1)


def test_accel_decel():
    pass


def test_blackwhite():
    # TODO update to BitmapClip
    clip = get_test_video()
    clip1 = blackwhite(clip)
    clip1.write_videofile(os.path.join(TMP_DIR, "blackwhite1.webm"))
    close_all_clips(locals())


# This currently fails with a with_mask error!
# def test_blink():
#     with VideoFileClip("media/big_buck_bunny_0_30.webm").subclip(0,10) as clip:
#       clip1 = blink(clip, 1, 1)
#       clip1.write_videofile(os.path.join(TMP_DIR,"blink1.webm"))


def test_colorx():
    color_dict = {"H": (0, 0, 200), "L": (0, 0, 50), "B": (0, 0, 255), "O": (0, 0, 0)}
    clip = BitmapClip([["LLO", "BLO"]], color_dict=color_dict).set_fps(1)

    clipfx = colorx(clip, 4)
    target = BitmapClip([["HHO", "BHO"]], color_dict=color_dict).set_fps(1)
    assert target == clipfx


def test_crop():
    # x: 0 -> 4, y: 0 -> 3 inclusive
    clip = BitmapClip([["ABCDE", "BCDEA", "CDEAB", "DEABC"]]).set_fps(1)

    clip1 = crop(clip)
    target1 = BitmapClip([["ABCDE", "BCDEA", "CDEAB", "DEABC"]]).set_fps(1)
    assert clip1 == target1

    clip2 = crop(clip, x1=1, y1=1, x2=3, y2=3)
    target2 = BitmapClip([["CD", "DE"]]).set_fps(1)
    assert clip2 == target2

    clip3 = crop(clip, y1=2)
    target3 = BitmapClip([["CDEAB", "DEABC"]]).set_fps(1)
    assert clip3 == target3

    clip4 = crop(clip, x1=2, width=2)
    target4 = BitmapClip([["CD", "DE", "EA", "AB"]]).set_fps(1)
    assert clip4 == target4

    # TODO x_center=1 does not perform correctly
    clip5 = crop(clip, x_center=2, y_center=2, width=3, height=3)
    target5 = BitmapClip([["ABC", "BCD", "CDE"]]).set_fps(1)
    assert clip5 == target5

    clip6 = crop(clip, x_center=2, width=2, y1=1, y2=2)
    target6 = BitmapClip([["CD"]]).set_fps(1)
    assert clip6 == target6


def test_even_size():
    clip1 = BitmapClip([["ABC", "BCD"]]).set_fps(1)  # Width odd
    clip1even = even_size(clip1)
    target1 = BitmapClip([["AB", "BC"]]).set_fps(1)
    assert clip1even == target1

    clip2 = BitmapClip([["AB", "BC", "CD"]]).set_fps(1)  # Height odd
    clip2even = even_size(clip2)
    target2 = BitmapClip([["AB", "BC"]]).set_fps(1)
    assert clip2even == target2

    clip3 = BitmapClip([["ABC", "BCD", "CDE"]]).set_fps(1)  # Width and height odd
    clip3even = even_size(clip3)
    target3 = BitmapClip([["AB", "BC"]]).set_fps(1)
    assert clip3even == target3

    pass


def test_even_size():
    clip1 = BitmapClip([["ABC", "BCD"]]).set_fps(1)  # Width odd
    clip1even = even_size(clip1)
    target1 = BitmapClip([["AB", "BC"]]).set_fps(1)
    assert clip1even == target1

    clip2 = BitmapClip([["AB", "BC", "CD"]]).set_fps(1)  # Height odd
    clip2even = even_size(clip2)
    target2 = BitmapClip([["AB", "BC"]]).set_fps(1)
    assert clip2even == target2

    clip3 = BitmapClip([["ABC", "BCD", "CDE"]]).set_fps(1)  # Width and height odd
    clip3even = even_size(clip3)
    target3 = BitmapClip([["AB", "BC"]]).set_fps(1)
    assert clip3even == target3

    pass


def test_fadein():
    clip = get_test_video()
    clip1 = fadein(clip, 0.5)
    clip1.write_videofile(os.path.join(TMP_DIR, "fadein1.webm"))
    close_all_clips(locals())


def test_fadeout():
    clip = get_test_video()
    clip1 = fadeout(clip, 0.5)
    clip1.write_videofile(os.path.join(TMP_DIR, "fadeout1.webm"))
    close_all_clips(locals())


def test_freeze():
    clip = BitmapClip([["R"], ["G"], ["B"]]).set_fps(1)  # 3 separate frames

    clip1 = freeze(clip, t=1, freeze_duration=1)
    target1 = BitmapClip([["R"], ["G"], ["G"], ["B"]]).set_fps(1)
    assert clip1 == target1

    clip2 = freeze(clip, t="end", freeze_duration=1)
    target2 = BitmapClip([["R"], ["G"], ["B"], ["B"]]).set_fps(1)
    assert clip2 == target2

    clip3 = freeze(clip, t=1, total_duration=4)
    target3 = BitmapClip([["R"], ["G"], ["G"], ["B"]]).set_fps(1)
    assert clip3 == target3

    clip4 = freeze(clip, t="end", total_duration=4, padding_end=1)
    target4 = BitmapClip([["R"], ["G"], ["G"], ["B"]]).set_fps(1)
    assert clip4 == target4


def test_freeze_region():
    pass


def test_gamma_corr():
    pass


def test_headblur():
    pass


def test_invert_colors():
    clip = BitmapClip(
        [["AB", "BC"]],
        color_dict={"A": (0, 0, 0), "B": (50, 100, 150), "C": (255, 255, 255)},
    ).set_fps(1)

    clip1 = invert_colors(clip)
    target1 = BitmapClip(
        [["CD", "DA"]],
        color_dict={"A": (0, 0, 0), "D": (205, 155, 105), "C": (255, 255, 255)},
    ).set_fps(1)
    assert clip1 == target1


def test_loop():
    clip = get_test_video()
    clip1 = loop(clip).set_duration(10)  # infinite looping
    clip1.write_videofile(os.path.join(TMP_DIR, "loop1.webm"))

    return  # Still buggy
    clip2 = loop(clip, duration=10)  # loop for 10 seconds
    clip2.write_videofile(os.path.join(TMP_DIR, "loop2.webm"))

    clip3 = loop(clip, n=3)  # loop 3 times
    clip3.write_videofile(os.path.join(TMP_DIR, "loop3.webm"))
    close_all_clips(objects=locals())


def test_lum_contrast():
    clip = get_test_video()
    clip1 = lum_contrast(clip)
    clip1.write_videofile(os.path.join(TMP_DIR, "lum_contrast1.webm"))
    close_all_clips(locals())

    # what are the correct value ranges for function arguments lum,
    # contrast and contrast_thr?  Maybe we should check for these in
    # lum_contrast.


def test_make_loopable():
    clip = get_test_video()
    clip1 = make_loopable(clip, 0.4)
    clip1.write_videofile(os.path.join(TMP_DIR, "make_loopable1.webm"))
    close_all_clips(locals())


def test_margin():
    clip = BitmapClip([["RRR", "RRR"], ["RRB", "RRB"]]).set_fps(1)

    # Make sure that the default values leave clip unchanged
    clip1 = margin(clip)
    assert clip == clip1

    # 1 pixel black margin
    clip2 = margin(clip, mar=1)
    target = BitmapClip(
        [["OOOOO", "ORRRO", "ORRRO", "OOOOO",], ["OOOOO", "ORRBO", "ORRBO", "OOOOO",],]
    ).set_fps(1)
    assert target == clip2

    # 1 pixel green margin
    clip3 = margin(clip, mar=1, color=(0, 255, 0))
    target = BitmapClip(
        [["GGGGG", "GRRRG", "GRRRG", "GGGGG",], ["GGGGG", "GRRBG", "GRRBG", "GGGGG",],]
    ).set_fps(1)
    assert target == clip3


def test_mask_and():
    pass


def test_mask_color():
    pass


def test_mask_or():
    pass


def test_mirror_x():
    clip = BitmapClip([["AB", "CD"]]).set_fps(1)
    clip1 = mirror_x(clip)
    target = BitmapClip([["BA", "DC"]]).set_fps(1)
    assert clip1 == target


def test_mirror_y():
    clip = BitmapClip([["AB", "CD"]]).set_fps(1)
    clip1 = mirror_y(clip)
    target = BitmapClip([["CD", "AB"]]).set_fps(1)
    assert clip1 == target


def test_painting():
    pass


def test_resize():
    # TODO update to BitmapClip
    clip = get_test_video()

    clip1 = resize(clip, (460, 720))  # New resolution: (460,720)
    assert clip1.size == (460, 720)
    clip1.write_videofile(os.path.join(TMP_DIR, "resize1.webm"))

    clip2 = resize(clip, 0.6)  # width and heigth multiplied by 0.6
    assert clip2.size == (clip.size[0] * 0.6, clip.size[1] * 0.6)
    clip2.write_videofile(os.path.join(TMP_DIR, "resize2.webm"))

    clip3 = resize(clip, width=800)  # height computed automatically.
    assert clip3.w == 800
    # assert clip3.h == ??
    clip3.write_videofile(os.path.join(TMP_DIR, "resize3.webm"))
    close_all_clips(locals())

    # I get a general stream error when playing this video.
    # clip4=clip.resize(lambda t : 1+0.02*t) # slow swelling of the clip
    # clip4.write_videofile(os.path.join(TMP_DIR, "resize4.webm"))


def test_rotate():
    # TODO update to BitmapClip
    clip = get_test_video()

    clip1 = rotate(clip, 90)  # rotate 90 degrees
    assert clip1.size == (clip.size[1], clip.size[0])
    clip1.write_videofile(os.path.join(TMP_DIR, "rotate1.webm"))

    clip2 = rotate(clip, 180)  # rotate 90 degrees
    assert clip2.size == tuple(clip.size)
    clip2.write_videofile(os.path.join(TMP_DIR, "rotate2.webm"))

    clip3 = rotate(clip, 270)  # rotate 90 degrees
    assert clip3.size == (clip.size[1], clip.size[0])
    clip3.write_videofile(os.path.join(TMP_DIR, "rotate3.webm"))

    clip4 = rotate(clip, 360)  # rotate 90 degrees
    assert clip4.size == tuple(clip.size)
    clip4.write_videofile(os.path.join(TMP_DIR, "rotate4.webm"))

    clip5 = rotate(clip, 50)
    clip5.write_videofile(os.path.join(TMP_DIR, "rotate5.webm"))

    # Test rotate with color clip
    clip = ColorClip([600, 400], [150, 250, 100]).set_duration(1).set_fps(5)
    clip = rotate(clip, 20)
    clip.write_videofile(os.path.join(TMP_DIR, "color_rotate.webm"))

    close_all_clips(locals())


def test_scroll():
    # clip = bitmap_to_clip([[""]])
    pass


def test_speedx():
    # TODO update to BitmapClip
    clip = get_test_video()

    clip1 = speedx(clip, factor=0.5)  # 1/2 speed
    assert clip1.duration == 2
    clip1.write_videofile(os.path.join(TMP_DIR, "speedx1.webm"))

    clip2 = speedx(clip, final_duration=2)  # 1/2 speed
    assert clip2.duration == 2
    clip2.write_videofile(os.path.join(TMP_DIR, "speedx2.webm"))

    clip2 = speedx(clip, final_duration=3)  # 1/3 speed
    assert clip2.duration == 3
    clip2.write_videofile(os.path.join(TMP_DIR, "speedx3.webm"))
    close_all_clips(locals())


def test_supersample():
    pass


def test_time_mirror():
    clip = BitmapClip([["AA", "AA"], ["BB", "BB"], ["CC", "CC"]]).set_fps(1)

    clip1 = time_mirror(clip)
    target1 = BitmapClip([["CC", "CC"], ["BB", "BB"], ["AA", "AA"]]).set_fps(1)
    assert clip1 == target1

    clip2 = BitmapClip(
        [["AA", "AA"], ["BB", "BB"], ["CC", "CC"], ["DD", "DD"]]
    ).set_fps(1)

    clip3 = time_mirror(clip2)
    target3 = BitmapClip(
        [["DD", "DD"], ["CC", "CC"], ["BB", "BB"], ["AA", "AA"]]
    ).set_fps(1)
    assert clip3 == target3


def test_time_symmetrize():
    clip = BitmapClip([["AA", "AA"], ["BB", "BB"], ["CC", "CC"]]).set_fps(1)

    clip1 = time_symmetrize(clip)
    target1 = BitmapClip(
        [
            ["AA", "AA"],
            ["BB", "BB"],
            ["CC", "CC"],
            ["CC", "CC"],
            ["BB", "BB"],
            ["AA", "AA"],
        ]
    ).set_fps(1)
    assert clip1 == target1


def test_normalize():
    clip = AudioFileClip("media/crunching.mp3")
    clip = audio_normalize(clip)
    assert clip.max_volume() == 1
    close_all_clips(locals())


if __name__ == "__main__":
    pytest.main()
