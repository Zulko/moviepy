import os
import sys

import pytest
from moviepy.utils import close_all_clips
from moviepy.video.fx.blackwhite import blackwhite
# from moviepy.video.fx.blink import blink
from moviepy.video.fx.colorx import colorx
from moviepy.video.fx.crop import crop
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
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
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip

sys.path.append("tests")

from . import download_media
from .test_helper import TMP_DIR


def test_download_media(capsys):
    with capsys.disabled():
        download_media.download()


def get_test_video():
    return VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0, 1)


def test_blackwhite():
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
    clip = get_test_video()
    clip1 = colorx(clip, 2)
    clip1.write_videofile(os.path.join(TMP_DIR, "colorx1.webm"))
    close_all_clips(locals())

def test_crop():
    clip = get_test_video()

    clip1 = crop(clip)  # ie, no cropping (just tests all default values)
    clip1.write_videofile(os.path.join(TMP_DIR, "crop1.webm"))

    clip2 = crop(clip, x1=50, y1=60, x2=460, y2=275)
    clip2.write_videofile(os.path.join(TMP_DIR, "crop2.webm"))

    clip3 = crop(clip, y1=30)  # remove part above y=30
    clip3.write_videofile(os.path.join(TMP_DIR, "crop3.webm"))

    clip4 = crop(clip, x1=10, width=200)  # crop a rect that has width=200
    clip4.write_videofile(os.path.join(TMP_DIR, "crop4.webm"))

    clip5 = crop(clip, x_center=300, y_center=400, width=50, height=150)
    clip5.write_videofile(os.path.join(TMP_DIR, "crop5.webm"))

    clip6 = crop(clip, x_center=300, width=400, y1=100, y2=600)
    clip6.write_videofile(os.path.join(TMP_DIR, "crop6.webm"))
    close_all_clips(locals())

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


def test_invert_colors():
    clip = get_test_video()
    clip1 = invert_colors(clip)
    clip1.write_videofile(os.path.join(TMP_DIR, "invert_colors1.webm"))
    close_all_clips(locals())


def test_loop():
    # these do not work..  what am I doing wrong??
    return

    clip = get_test_video()
    clip1 = clip.loop()  # infinite looping
    clip1.write_videofile(os.path.join(TMP_DIR, "loop1.webm"))

    clip2 = clip.loop(duration=10)  # loop for 10 seconds
    clip2.write_videofile(os.path.join(TMP_DIR, "loop2.webm"))

    clip3 = clip.loop(n=3)  # loop 3 times
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
    clip = get_test_video()
    clip1 = margin(clip)  # does the default values change anything?
    clip1.write_videofile(os.path.join(TMP_DIR, "margin1.webm"))

    clip2 = margin(clip, mar=100)  # all margins are 100px
    clip2.write_videofile(os.path.join(TMP_DIR, "margin2.webm"))

    clip3 = margin(clip, mar=100, color=(255, 0, 0))  # red margin
    clip3.write_videofile(os.path.join(TMP_DIR, "margin3.webm"))
    close_all_clips(locals())


def test_mask_and():
    pass


def test_mask_color():
    pass


def test_mask_or():
    pass


def test_mirror_x():
    clip = get_test_video()
    clip1 = mirror_x(clip)
    clip1.write_videofile(os.path.join(TMP_DIR, "mirror_x1.webm"))
    close_all_clips(locals())


def test_mirror_y():
    clip = get_test_video()
    clip1 = mirror_y(clip)
    clip1.write_videofile(os.path.join(TMP_DIR, "mirror_y1.webm"))
    close_all_clips(locals())


def test_painting():
    pass


def test_resize():
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
    #clip4.write_videofile(os.path.join(TMP_DIR, "resize4.webm"))


def test_rotate():
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
    close_all_clips(locals())


def test_scroll():
    pass


def test_speedx():
    clip = get_test_video()

    clip1 = speedx(clip, factor=0.5)  # 1/2 speed
    assert clip1.duration == 2
    clip1.write_videofile(os.path.join(TMP_DIR, "speedx1.webm"))

    clip2 = speedx(clip, final_duration=2)  # 1/2 speed
    assert clip2.duration == 2
    clip2.write_videofile(os.path.join(TMP_DIR, "speedx2.webm"))

    clip2 = speedx(clip, final_duration=3)  # 1/2 speed
    assert clip2.duration == 3
    clip2.write_videofile(os.path.join(TMP_DIR, "speedx3.webm"))
    close_all_clips(locals())


def test_supersample():
    pass


def test_time_mirror():
    clip = get_test_video()

    clip1 = time_mirror(clip)
    assert clip1.duration == clip.duration
    clip1.write_videofile(os.path.join(TMP_DIR, "time_mirror1.webm"))
    close_all_clips(locals())


def test_time_symmetrize():
    clip = get_test_video()

    clip1 = time_symmetrize(clip)
    clip1.write_videofile(os.path.join(TMP_DIR, "time_symmetrize1.webm"))
    close_all_clips(locals())


def test_normalize():
    clip = AudioFileClip('media/crunching.mp3')
    clip = audio_normalize(clip)
    assert clip.max_volume() == 1
    close_all_clips(locals())


if __name__ == '__main__':
    pytest.main()
