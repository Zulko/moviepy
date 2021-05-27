from moviepy import *


# UKULELE CLIP, OBTAINED BY CUTTING AND CROPPING
# RAW FOOTAGE

ukulele = (
    VideoFileClip("../../videos/moi_ukulele.MOV", audio=False)
    .subclip(60 + 33, 60 + 50)
    .crop(486, 180, 1196, 570)
)

w, h = moviesize = ukulele.size

# THE PIANO FOOTAGE IS DOWNSIZED, HAS A WHITE MARGIN, IS
# IN THE BOTTOM RIGHT CORNER

piano = (
    VideoFileClip("../../videos/douceamb.mp4", audio=False)
    .subclip(30, 50)
    .resize((w / 3, h / 3))
    .margin(6, color=(255, 255, 255))  # one third of the total screen
    .margin(bottom=20, right=20, opacity=0)  # white margin
    .set_pos(("right", "bottom"))  # transparent
)


# A CLIP WITH A TEXT AND A BLACK SEMI-OPAQUE BACKGROUND

txt = TextClip(
    "V. Zulkoninov - Ukulele Sonata", font="Amiri-regular", color="white", font_size=24
)

txt_col = txt.on_color(
    size=(ukulele.w + txt.w, txt.h - 10),
    color=(0, 0, 0),
    pos=(6, "center"),
    col_opacity=0.6,
)


# THE TEXT CLIP IS ANIMATED.
# I am *NOT* explaining the formula, understands who can/want.
txt_mov = txt_col.set_pos(
    lambda t: (max(w / 30, int(w - 0.5 * w * t)), max(5 * h / 6, int(100 * t)))
)


# FINAL ASSEMBLY
final = CompositeVideoClip([ukulele, txt_mov, piano])
final.subclip(0, 5).write_videofile("../../ukulele.avi", fps=24, codec="libx264")
