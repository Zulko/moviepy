import os

import pytest

from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.utils import close_all_clips
from moviepy.video.VideoClip import BitmapClip, ColorClip
from moviepy.video.fx.blackwhite import blackwhite
from moviepy.video.fx.blink import blink
from moviepy.video.fx.colorx import colorx
from moviepy.video.fx.crop import crop
from moviepy.video.fx.even_size import even_size
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.freeze import freeze
from moviepy.video.fx.freeze_region import freeze_region
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
from moviepy.video.VideoClip import ColorClip

from tests.test_helper import TMP_DIR


def get_test_video():
    return VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0, 1)


def test_accel_decel():
    pass


def test_blackwhite():
    # TODO update to use BitmapClip
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
    clip = BitmapClip([["ABCDE", "EDCBA", "CDEAB", "BAEDC"]]).set_fps(1)

    clip1 = crop(clip)
    target1 = BitmapClip([["ABCDE", "EDCBA", "CDEAB", "BAEDC"]]).set_fps(1)
    assert clip1 == target1

    clip2 = crop(clip, x1=1, y1=1, x2=3, y2=3)
    target2 = BitmapClip([["DC", "DE"]]).set_fps(1)
    assert clip2 == target2

    clip3 = crop(clip, y1=2)
    target3 = BitmapClip([["CDEAB", "BAEDC"]]).set_fps(1)
    assert clip3 == target3

    clip4 = crop(clip, x1=2, width=2)
    target4 = BitmapClip([["CD", "CB", "EA", "ED"]]).set_fps(1)
    assert clip4 == target4

    # TODO x_center=1 does not perform correctly
    clip5 = crop(clip, x_center=2, y_center=2, width=3, height=3)
    target5 = BitmapClip([["ABC", "EDC", "CDE"]]).set_fps(1)
    assert clip5 == target5

    clip6 = crop(clip, x_center=2, width=2, y1=1, y2=2)
    target6 = BitmapClip([["DC"]]).set_fps(1)
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
    clip = BitmapClip([["AAB", "CCC"], ["BBR", "DDD"], ["CCC", "ABC"]]).set_fps(1)

    # Test region
    clip1 = freeze_region(clip, t=1, region=(2, 0, 3, 1))
    target1 = BitmapClip([["AAR", "CCC"], ["BBR", "DDD"], ["CCR", "ABC"]]).set_fps(1)
    assert clip1 == target1

    # Test outside_region
    clip2 = freeze_region(clip, t=1, outside_region=(2, 0, 3, 1))
    target2 = BitmapClip([["BBB", "DDD"], ["BBR", "DDD"], ["BBC", "DDD"]]).set_fps(1)
    assert clip2 == target2

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
    clip1 = loop(clip).set_duration(3)  # infinite looping
    clip1.write_videofile(os.path.join(TMP_DIR, "loop1.webm"))

    return  # Still buggy. TODO fix
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
    # TODO update to use BitmapClip
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


@pytest.mark.parametrize("angle_offset", [-360, 0, 360, 720])
def test_rotate(angle_offset):
    # Run several times to ensure that adding 360 to rotation angles has no effect
    clip = BitmapClip([["AAAA", "BBBB", "CCCC"], ["ABCD", "BCDE", "CDEA"]]).set_fps(1)

    clip1 = rotate(clip, 0 + angle_offset)
    target1 = BitmapClip([["AAAA", "BBBB", "CCCC"], ["ABCD", "BCDE", "CDEA"]]).set_fps(
        1
    )
    assert clip1 == target1

    clip2 = rotate(clip, 90 + angle_offset)
    target2 = BitmapClip(
        [["ABC", "ABC", "ABC", "ABC"], ["DEA", "CDE", "BCD", "ABC"]]
    ).set_fps(1)
    assert clip2 == target2, clip2.to_bitmap()

    clip3 = rotate(clip, 180 + angle_offset)
    target3 = BitmapClip([["CCCC", "BBBB", "AAAA"], ["AEDC", "EDCB", "DCBA"]]).set_fps(
        1
    )
    assert clip3 == target3

    clip4 = rotate(clip, 270 + angle_offset)
    target4 = BitmapClip(
        [["CBA", "CBA", "CBA", "CBA"], ["CBA", "DCB", "EDC", "AED"]]
    ).set_fps(1)
    assert clip4 == target4


def test_rotate_nonstandard_angles():
    # Test rotate with color clip
    clip = ColorClip([600, 400], [150, 250, 100]).set_duration(1).set_fps(5)
    clip = rotate(clip, 20)
    clip.write_videofile(os.path.join(TMP_DIR, "color_rotate.webm"))


def test_scroll():
    pass


def test_speedx():
    clip = BitmapClip([["A"], ["B"], ["C"], ["D"]]).set_fps(1)

    clip1 = speedx(clip, 0.5)  # 1/2x speed
    target1 = BitmapClip(
        [["A"], ["A"], ["B"], ["B"], ["C"], ["C"], ["D"], ["D"]]
    ).set_fps(1)
    assert clip1 == target1

    clip2 = speedx(clip, final_duration=8)  # 1/2x speed
    target2 = BitmapClip(
        [["A"], ["A"], ["B"], ["B"], ["C"], ["C"], ["D"], ["D"]]
    ).set_fps(1)
    assert clip2 == target2

    clip3 = speedx(clip, final_duration=12)  # 1/2x speed
    target3 = BitmapClip(
        [
            ["A"],
            ["A"],
            ["A"],
            ["B"],
            ["B"],
            ["B"],
            ["C"],
            ["C"],
            ["C"],
            ["D"],
            ["D"],
            ["D"],
        ]
    ).set_fps(1)
    assert clip3 == target3

    clip4 = speedx(clip, 2)  # 2x speed
    target4 = BitmapClip([["A"], ["C"]]).set_fps(1)
    assert clip4 == target4

    clip5 = speedx(clip, final_duration=2)  # 2x speed
    target5 = BitmapClip([["A"], ["C"]]).set_fps(1)
    assert clip5 == target5

    clip6 = speedx(clip, 4)  # 4x speed
    target6 = BitmapClip([["A"]]).set_fps(1)
    assert (
        clip6 == target6
    ), f"{clip6.duration} {target6.duration} {clip6.fps} {target6.fps}"


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
