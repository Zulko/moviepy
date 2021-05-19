"""Requires scikit-image installed (for ``vfx.painting``)."""

from moviepy import *


# WE TAKE THE SUBCLIPS WHICH ARE 2 SECONDS BEFORE & AFTER THE FREEZE

charade = VideoFileClip("../../videos/charade.mp4")
tfreeze = convert_to_seconds(19.21)  # Time of the freeze, 19'21

clip_before = charade.subclip(tfreeze - 2, tfreeze)
clip_after = charade.subclip(tfreeze, tfreeze + 2)


# THE FRAME TO FREEZE

im_freeze = charade.to_ImageClip(tfreeze)
painting = charade.fx(vfx.painting, saturation=1.6, black=0.006).to_ImageClip(tfreeze)

txt = TextClip("Audrey", font="Amiri-regular", font_size=35)

painting_txt = (
    CompositeVideoClip([painting, txt.set_pos((10, 180))])
    .add_mask()
    .with_duration(3)
    .crossfadein(0.5)
    .crossfadeout(0.5)
)

# FADEIN/FADEOUT EFFECT ON THE PAINTED IMAGE

painting_fading = CompositeVideoClip([im_freeze, painting_txt])

# FINAL CLIP AND RENDERING

final_clip = concatenate_videoclips(
    [clip_before, painting_fading.with_duration(3), clip_after]
)

final_clip.write_videofile(
    "../../audrey.avi", fps=charade.fps, codec="mpeg4", audio_bitrate="3000k"
)
