import os
import random

import numpy as np
import pytest

from moviepy import AudioClip, AudioFileClip, BitmapClip, ColorClip, VideoFileClip
from moviepy.audio.fx import audio_normalize, multiply_stereo_volume
from moviepy.utils import close_all_clips
from moviepy.video.fx import (
    blackwhite,
    crop,
    even_size,
    fadein,
    fadeout,
    freeze,
    freeze_region,
    invert_colors,
    loop,
    lum_contrast,
    make_loopable,
    margin,
    mirror_x,
    mirror_y,
    multiply_color,
    resize,
    rotate,
    speedx,
    time_mirror,
    time_symmetrize,
)

from tests.test_helper import TMP_DIR


def get_test_video():
    return VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0, 1)


def test_accel_decel():
    pass


def test_blackwhite():
    # Create black/white spectrum ``bw_color_dict`` to compare against it.
    # Colors after ``blackwhite`` FX must be inside this dictionary
    # Note: black/white spectrum is made of colors with same numbers
    # [(0, 0, 0), (1, 1, 1), (2, 2, 2)...]
    bw_color_dict = {}
    for num in range(0, 256):
        bw_color_dict[chr(num + 255)] = (num, num, num)
    color_dict = bw_color_dict.copy()
    # update dictionary with default BitmapClip color_dict values
    color_dict.update(BitmapClip.DEFAULT_COLOR_DICT)

    # add row with random colors in b/w spectrum
    random_row = ""
    for num in range(512, 515):
        # use unique unicode representation for each color
        char = chr(num)
        random_row += char

        # random colors in the b/w spectrum
        color_dict[char] = tuple(random.randint(0, 255) for i in range(3))

    # clip converted below to black/white
    clip = BitmapClip([["RGB", random_row]], color_dict=color_dict, fps=1)

    # for each possible ``preserve_luminosity`` boolean argument value
    for preserve_luminosity in [True, False]:
        # default argument (``RGB=None``)
        clip_bw = blackwhite(clip, preserve_luminosity=preserve_luminosity)

        bitmap = clip_bw.to_bitmap()
        assert bitmap

        for i, row in enumerate(bitmap[0]):
            for char in row:
                # all characters returned by ``to_bitmap`` are in the b/w spectrum
                assert char in bw_color_dict

                if i == 0:  # pure "RGB" colors are converted to [85, 85, 85]
                    assert char == row[0]  # so are equal

        # custom random ``RGB`` argument
        clip_bw_custom_rgb = blackwhite(
            clip,
            RGB=(random.randint(0, 255), 0, 0),
            preserve_luminosity=preserve_luminosity,
        )
        bitmap = clip_bw_custom_rgb.to_bitmap()
        for i, row in enumerate(bitmap[0]):
            for i2, char in enumerate(row):
                # all characters returned by ``to_bitmap`` are in the b/w spectrum
                assert char in bw_color_dict

                # for clip "RGB" row, two latest converted colors are equal
                if i == 0 and i2 > 0:
                    assert char == row[1] and char == row[2]

        # ``RGB="CRT_phosphor"`` argument
        clip_bw_crt_phosphor = blackwhite(
            clip, RGB="CRT_phosphor", preserve_luminosity=preserve_luminosity
        )
        bitmap = clip_bw_crt_phosphor.to_bitmap()
        assert bitmap
        for row in bitmap[0]:
            for char in row:
                # all characters returned by ``to_bitmap`` are in the b/w spectrum
                assert char in bw_color_dict

    close_all_clips(locals())


# This currently fails with a with_mask error!
# def test_blink():
#     with VideoFileClip("media/big_buck_bunny_0_30.webm").subclip(0,10) as clip:
#       clip1 = blink(clip, 1, 1)
#       clip1.write_videofile(os.path.join(TMP_DIR,"blink1.webm"))


def test_multiply_color():
    color_dict = {"H": (0, 0, 200), "L": (0, 0, 50), "B": (0, 0, 255), "O": (0, 0, 0)}
    clip = BitmapClip([["LLO", "BLO"]], color_dict=color_dict, fps=1)

    clipfx = multiply_color(clip, 4)
    target = BitmapClip([["HHO", "BHO"]], color_dict=color_dict, fps=1)
    assert target == clipfx


def test_crop():
    # x: 0 -> 4, y: 0 -> 3 inclusive
    clip = BitmapClip([["ABCDE", "EDCBA", "CDEAB", "BAEDC"]], fps=1)

    clip1 = crop(clip)
    target1 = BitmapClip([["ABCDE", "EDCBA", "CDEAB", "BAEDC"]], fps=1)
    assert clip1 == target1

    clip2 = crop(clip, x1=1, y1=1, x2=3, y2=3)
    target2 = BitmapClip([["DC", "DE"]], fps=1)
    assert clip2 == target2

    clip3 = crop(clip, y1=2)
    target3 = BitmapClip([["CDEAB", "BAEDC"]], fps=1)
    assert clip3 == target3

    clip4 = crop(clip, x1=2, width=2)
    target4 = BitmapClip([["CD", "CB", "EA", "ED"]], fps=1)
    assert clip4 == target4

    # TODO x_center=1 does not perform correctly
    clip5 = crop(clip, x_center=2, y_center=2, width=3, height=3)
    target5 = BitmapClip([["ABC", "EDC", "CDE"]], fps=1)
    assert clip5 == target5

    clip6 = crop(clip, x_center=2, width=2, y1=1, y2=2)
    target6 = BitmapClip([["DC"]], fps=1)
    assert clip6 == target6


def test_even_size():
    clip1 = BitmapClip([["ABC", "BCD"]], fps=1)  # Width odd
    clip1even = even_size(clip1)
    target1 = BitmapClip([["AB", "BC"]], fps=1)
    assert clip1even == target1

    clip2 = BitmapClip([["AB", "BC", "CD"]], fps=1)  # Height odd
    clip2even = even_size(clip2)
    target2 = BitmapClip([["AB", "BC"]], fps=1)
    assert clip2even == target2

    clip3 = BitmapClip([["ABC", "BCD", "CDE"]], fps=1)  # Width and height odd
    clip3even = even_size(clip3)
    target3 = BitmapClip([["AB", "BC"]], fps=1)
    assert clip3even == target3


def test_fadein():
    color_dict = {
        "I": (0, 0, 0),
        "R": (255, 0, 0),
        "G": (0, 255, 0),
        "B": (0, 0, 255),
        "W": (255, 255, 255),
    }
    clip = BitmapClip([["R"], ["G"], ["B"]], color_dict=color_dict, fps=1)

    clip1 = fadein(clip, 1)  # default initial color
    target1 = BitmapClip([["I"], ["G"], ["B"]], color_dict=color_dict, fps=1)
    assert clip1 == target1

    clip2 = fadein(clip, 1, initial_color=(255, 255, 255))  # different initial color
    target2 = BitmapClip([["W"], ["G"], ["B"]], color_dict=color_dict, fps=1)
    assert clip2 == target2


def test_fadeout():
    clip = get_test_video()
    clip1 = fadeout(clip, 0.5)
    clip1.write_videofile(os.path.join(TMP_DIR, "fadeout1.webm"))
    close_all_clips(locals())


@pytest.mark.parametrize(
    (
        "t",
        "freeze_duration",
        "total_duration",
        "padding_end",
        "output_frames",
    ),
    (
        # at start, 1 second (default t == 0)
        (
            None,
            1,
            None,
            None,
            ["R", "R", "G", "B"],
        ),
        # at start, 1 second (explicit t)
        (
            0,
            1,
            None,
            None,
            ["R", "R", "G", "B"],
        ),
        # at end, 1 second
        (
            "end",
            1,
            None,
            None,
            ["R", "G", "B", "B"],
        ),
        # at end 1 second, padding end 1 second
        (
            "end",
            1,
            None,
            1,
            ["R", "G", "G", "B"],
        ),
        # at 2nd frame, 1 second
        (
            1,  # second 0 is frame 1, second 1 is frame 2...
            1,
            None,
            None,
            ["R", "G", "G", "B"],
        ),
        # at 2nd frame, 2 seconds
        (
            1,
            2,
            None,
            None,
            ["R", "G", "G", "G", "B"],
        ),
        # `freeze_duration`, `total_duration` are None
        (1, None, None, None, ValueError),
        # `total_duration` 5 at start (2 seconds)
        (None, None, 5, None, ["R", "R", "R", "G", "B"]),
        # total duration 5 at end
        ("end", None, 5, None, ["R", "G", "B", "B", "B"]),
        # total duration 5 padding end
        ("end", None, 5, 1, ["R", "G", "G", "G", "B"]),
    ),
    ids=[
        "at start, 1 second (default t == 0)",
        "at start, 1 second (explicit t)",
        "at end, 1 second",
        "at end 1 second, padding end 1 second",
        "at 2nd frame, 1 second",
        "at 2nd frame, 2 seconds",
        "`freeze_duration`, `total_duration` are None",
        "`total_duration` 5 at start (2 seconds)",
        "`total_duration` 5 at end",
        "`total_duration` 5 padding end",
    ],
)
def test_freeze(t, freeze_duration, total_duration, padding_end, output_frames):
    input_frames = ["R", "G", "B"]
    clip_duration = len(input_frames)

    # create BitmapClip with predefined set of colors, during 1 second each one
    clip = BitmapClip([list(color) for color in input_frames], fps=1).with_duration(
        clip_duration
    )

    # build kwargs passed to `freeze`
    possible_kwargs = {
        "t": t,
        "freeze_duration": freeze_duration,
        "total_duration": total_duration,
        "padding_end": padding_end,
    }
    kwargs = {
        kw_name: kw_value
        for kw_name, kw_value in possible_kwargs.items()
        if kw_value is not None
    }

    # freeze clip
    if hasattr(output_frames, "__traceback__"):
        with pytest.raises(output_frames):
            freeze(clip, **kwargs)
        return
    else:
        freezed_clip = freeze(clip, **kwargs)

    # assert new duration
    expected_freeze_duration = (
        freeze_duration
        if freeze_duration is not None
        else total_duration - clip_duration
    )
    assert freezed_clip.duration == clip_duration + expected_freeze_duration

    # assert colors are the expected
    for i, color in enumerate(freezed_clip.iter_frames()):
        expected_color = list(BitmapClip.DEFAULT_COLOR_DICT[output_frames[i]])
        assert list(color[0][0]) == expected_color


def test_freeze_region():
    clip = BitmapClip([["AAB", "CCC"], ["BBR", "DDD"], ["CCC", "ABC"]], fps=1)

    # Test region
    clip1 = freeze_region(clip, t=1, region=(2, 0, 3, 1))
    target1 = BitmapClip([["AAR", "CCC"], ["BBR", "DDD"], ["CCR", "ABC"]], fps=1)
    assert clip1 == target1

    # Test outside_region
    clip2 = freeze_region(clip, t=1, outside_region=(2, 0, 3, 1))
    target2 = BitmapClip([["BBB", "DDD"], ["BBR", "DDD"], ["BBC", "DDD"]], fps=1)
    assert clip2 == target2


def test_gamma_corr():
    pass


def test_headblur():
    pass


def test_invert_colors():
    clip = BitmapClip(
        [["AB", "BC"]],
        color_dict={"A": (0, 0, 0), "B": (50, 100, 150), "C": (255, 255, 255)},
        fps=1,
    )

    clip1 = invert_colors(clip)
    target1 = BitmapClip(
        [["CD", "DA"]],
        color_dict={"A": (0, 0, 0), "D": (205, 155, 105), "C": (255, 255, 255)},
        fps=1,
    )
    assert clip1 == target1


def test_loop():
    clip = BitmapClip([["R"], ["G"], ["B"]], fps=1)

    clip1 = loop(clip, n=2)  # loop 2 times
    target1 = BitmapClip([["R"], ["G"], ["B"], ["R"], ["G"], ["B"]], fps=1)
    assert clip1 == target1

    clip2 = loop(clip, duration=8)  # loop 8 seconds
    target2 = BitmapClip(
        [["R"], ["G"], ["B"], ["R"], ["G"], ["B"], ["R"], ["G"]], fps=1
    )
    assert clip2 == target2

    clip3 = loop(clip).with_duration(5)  # infinite loop
    target3 = BitmapClip([["R"], ["G"], ["B"], ["R"], ["G"]], fps=1)
    assert clip3 == target3

    clip = get_test_video().subclip(0.2, 0.3)  # 0.1 seconds long
    clip1 = loop(clip).with_duration(0.5)  # infinite looping
    clip1.write_videofile(os.path.join(TMP_DIR, "loop1.webm"))

    clip2 = loop(clip, duration=0.5)  # loop for 1 second
    clip2.write_videofile(os.path.join(TMP_DIR, "loop2.webm"))

    clip3 = loop(clip, n=3)  # loop 3 times
    clip3.write_videofile(os.path.join(TMP_DIR, "loop3.webm"))

    # Test audio looping
    clip = AudioClip(
        lambda t: np.sin(440 * 2 * np.pi * t) * (t % 1) + 0.5, duration=2.5, fps=44100
    )
    clip1 = clip.loop(2)
    # TODO fix AudioClip.__eq__()
    # assert concatenate_audioclips([clip, clip]) == clip1

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
    clip = BitmapClip([["RRR", "RRR"], ["RRB", "RRB"]], fps=1)

    # Make sure that the default values leave clip unchanged
    clip1 = margin(clip)
    assert clip == clip1

    # 1 pixel black margin
    clip2 = margin(clip, margin_size=1)
    target = BitmapClip(
        [["OOOOO", "ORRRO", "ORRRO", "OOOOO"], ["OOOOO", "ORRBO", "ORRBO", "OOOOO"]],
        fps=1,
    )
    assert target == clip2

    # 1 pixel green margin
    clip3 = margin(clip, margin_size=1, color=(0, 255, 0))
    target = BitmapClip(
        [["GGGGG", "GRRRG", "GRRRG", "GGGGG"], ["GGGGG", "GRRBG", "GRRBG", "GGGGG"]],
        fps=1,
    )
    assert target == clip3


def test_mask_and():
    pass


def test_mask_color():
    pass


def test_mask_or():
    pass


def test_mirror_x():
    clip = BitmapClip([["AB", "CD"]], fps=1)
    clip1 = mirror_x(clip)
    target = BitmapClip([["BA", "DC"]], fps=1)
    assert clip1 == target


def test_mirror_y():
    clip = BitmapClip([["AB", "CD"]], fps=1)
    clip1 = mirror_y(clip)
    target = BitmapClip([["CD", "AB"]], fps=1)
    assert clip1 == target


def test_painting():
    pass


def test_resize():
    # TODO update to use BitmapClip
    clip = get_test_video().subclip(0.2, 0.3)

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
    clip = BitmapClip([["AAAA", "BBBB", "CCCC"], ["ABCD", "BCDE", "CDEA"]], fps=1)

    clip1 = rotate(clip, 0 + angle_offset)
    target1 = BitmapClip([["AAAA", "BBBB", "CCCC"], ["ABCD", "BCDE", "CDEA"]], fps=1)
    assert clip1 == target1

    clip2 = rotate(clip, 90 + angle_offset)
    target2 = BitmapClip(
        [["ABC", "ABC", "ABC", "ABC"], ["DEA", "CDE", "BCD", "ABC"]], fps=1
    )
    assert clip2 == target2, clip2.to_bitmap()

    clip3 = rotate(clip, 180 + angle_offset)
    target3 = BitmapClip([["CCCC", "BBBB", "AAAA"], ["AEDC", "EDCB", "DCBA"]], fps=1)
    assert clip3 == target3

    clip4 = rotate(clip, 270 + angle_offset)
    target4 = BitmapClip(
        [["CBA", "CBA", "CBA", "CBA"], ["CBA", "DCB", "EDC", "AED"]], fps=1
    )
    assert clip4 == target4


def test_rotate_nonstandard_angles():
    # Test rotate with color clip
    clip = ColorClip([600, 400], [150, 250, 100]).with_duration(1).with_fps(5)
    clip = rotate(clip, 20)
    clip.write_videofile(os.path.join(TMP_DIR, "color_rotate.webm"))


def test_scroll():
    pass


def test_speedx():
    clip = BitmapClip([["A"], ["B"], ["C"], ["D"]], fps=1)

    clip1 = speedx(clip, 0.5)  # 1/2x speed
    target1 = BitmapClip(
        [["A"], ["A"], ["B"], ["B"], ["C"], ["C"], ["D"], ["D"]], fps=1
    )
    assert clip1 == target1

    clip2 = speedx(clip, final_duration=8)  # 1/2x speed
    target2 = BitmapClip(
        [["A"], ["A"], ["B"], ["B"], ["C"], ["C"], ["D"], ["D"]], fps=1
    )
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
        ],
        fps=1,
    )
    assert clip3 == target3

    clip4 = speedx(clip, 2)  # 2x speed
    target4 = BitmapClip([["A"], ["C"]], fps=1)
    assert clip4 == target4

    clip5 = speedx(clip, final_duration=2)  # 2x speed
    target5 = BitmapClip([["A"], ["C"]], fps=1)
    assert clip5 == target5

    clip6 = speedx(clip, 4)  # 4x speed
    target6 = BitmapClip([["A"]], fps=1)
    assert (
        clip6 == target6
    ), f"{clip6.duration} {target6.duration} {clip6.fps} {target6.fps}"


def test_supersample():
    pass


def test_time_mirror():
    clip = BitmapClip([["AA", "AA"], ["BB", "BB"], ["CC", "CC"]], fps=1)

    clip1 = time_mirror(clip)
    target1 = BitmapClip([["CC", "CC"], ["BB", "BB"], ["AA", "AA"]], fps=1)
    assert clip1 == target1

    clip2 = BitmapClip([["AA", "AA"], ["BB", "BB"], ["CC", "CC"], ["DD", "DD"]], fps=1)

    clip3 = time_mirror(clip2)
    target3 = BitmapClip(
        [["DD", "DD"], ["CC", "CC"], ["BB", "BB"], ["AA", "AA"]], fps=1
    )
    assert clip3 == target3


def test_time_symmetrize():
    clip = BitmapClip([["AA", "AA"], ["BB", "BB"], ["CC", "CC"]], fps=1)

    clip1 = time_symmetrize(clip)
    target1 = BitmapClip(
        [
            ["AA", "AA"],
            ["BB", "BB"],
            ["CC", "CC"],
            ["CC", "CC"],
            ["BB", "BB"],
            ["AA", "AA"],
        ],
        fps=1,
    )
    assert clip1 == target1


def test_audio_normalize():
    clip = AudioFileClip("media/crunching.mp3")
    clip = audio_normalize(clip)
    assert clip.max_volume() == 1
    close_all_clips(locals())


def test_audio_normalize_muted():
    z_array = np.array([0.0])
    make_frame = lambda t: z_array
    clip = AudioClip(make_frame, duration=1, fps=44100)
    clip = audio_normalize(clip)
    assert np.array_equal(clip.to_soundarray(), z_array)

    close_all_clips(locals())


def test_multiply_stereo_volume():
    clip = AudioFileClip("media/crunching.mp3")

    # mute
    clip_left_channel_muted = multiply_stereo_volume(clip, left=0)
    clip_right_channel_muted = multiply_stereo_volume(clip, right=0, left=2)

    left_channel_muted = clip_left_channel_muted.to_soundarray()[:, 0]
    right_channel_muted = clip_right_channel_muted.to_soundarray()[:, 1]

    z_channel = np.zeros(len(left_channel_muted))

    assert np.array_equal(left_channel_muted, z_channel)
    assert np.array_equal(right_channel_muted, z_channel)

    # double level
    left_channel_doubled = clip_right_channel_muted.to_soundarray()[:, 0]
    d_channel = clip.to_soundarray()[:, 0] * 2
    assert np.array_equal(left_channel_doubled, d_channel)

    # mono muted
    sinus_wave = lambda t: [np.sin(440 * 2 * np.pi * t)]
    mono_clip = AudioClip(sinus_wave, duration=2, fps=22050)
    muted_mono_clip = multiply_stereo_volume(mono_clip, left=0)
    mono_channel_muted = muted_mono_clip.to_soundarray()

    z_channel = np.zeros(len(mono_channel_muted))
    assert np.array_equal(mono_channel_muted, z_channel)

    # mono doubled
    mono_clip = AudioClip(sinus_wave, duration=2, fps=22050)
    doubled_mono_clip = multiply_stereo_volume(
        mono_clip, left=None, right=2
    )  # using right
    mono_channel_doubled = doubled_mono_clip.to_soundarray()
    d_channel = mono_clip.to_soundarray() * 2
    assert np.array_equal(mono_channel_doubled, d_channel)

    close_all_clips(locals())


if __name__ == "__main__":
    pytest.main()
