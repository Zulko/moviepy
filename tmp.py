from moviepy.editor import *
import numpy as np


def angle(t):
    return 0 if t >= d - 1 / 30 else 50 * (t + 1)


d = 3

clip = (
    TextClip(
        "text", font="Arial-Bold", fontsize=50, color="white", bg_color="transparent"
    )
    .set_duration(d)
    .rotate(angle)
)
clip = vfx.resize(clip, (256, 128))

clip.fx(vfx.freeze, t="end", freeze_duration=2).preview()

clip.write_videofile("tmp.mp4", codec="libx264", fps=30)

mainclip = VideoFileClip("tmp.mp4")

print("Image:")
mainclip.to_ImageClip(mainclip.duration).set_duration(5).preview()
print("Image done")

mainclip = mainclip.fx(vfx.freeze, t="end", freeze_duration=2)

mainclip.write_videofile("tmp2.mp4", fps=30, codec="libx264")

mainclip.preview()

"""clip = VideoFileClip("media/fire2.mp4").without_audio()
#clip.preview()
#t = clip.duration
#print(t)
#clip = clip.to_ImageClip(t).set_duration(5)

#clip.preview()

#clip = clip.fx(vfx.freeze, t="end", freeze_duration=2)
clip = vfx.freeze(clip, t="end", freeze_duration=20)
clip.preview()"""


def test_freeze():
    clip = BitmapClip([["R"], ["G"], ["B"]], fps=1)  # 3 separate frames

    clip1 = vfx.freeze(clip, t=1, freeze_duration=1)
    target1 = BitmapClip([["R"], ["G"], ["G"], ["B"]], fps=1)
    assert clip1 == target1

    clip2 = vfx.freeze(clip, t="end", freeze_duration=1)
    target2 = BitmapClip([["R"], ["G"], ["B"], ["B"]], fps=1)
    assert clip2 == target2

    clip3 = vfx.freeze(clip, t=1, total_duration=4)
    target3 = BitmapClip([["R"], ["G"], ["G"], ["B"]], fps=1)
    assert clip3 == target3

    clip4 = vfx.freeze(clip, t="end", total_duration=4, padding_end=2)
    target4 = BitmapClip([["R"], ["G"], ["G"], ["B"]], fps=1)
    # clip4.preview()

    for i in range(4):
        frame = clip4.get_frame(i)

    assert clip4 == target4


# test_freeze()
