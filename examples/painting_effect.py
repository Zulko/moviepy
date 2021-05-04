"""Requires scikit-image installed (for ``vfx.painting``)."""

from moviepy import *

# WE TAKE THE SUBCLIPS WHICH ARE 2 SECONDS BEFORE & AFTER THE FREEZE

test_video = VideoFileClip("media/audrey.mp4")
tfreeze = convert_to_seconds(3)  # Time of the freeze, 3 seconds

clip_before = test_video.subclip(tfreeze - 2, tfreeze)
clip_after = test_video.subclip(tfreeze, tfreeze + 2)

# THE FRAME TO FREEZE

im_freeze = test_video.to_ImageClip(tfreeze)
painting = test_video.fx(vfx.painting, saturation=1.6, black=0.006).to_ImageClip(tfreeze)


txt = TextClip("Audrey", font="Amiri-regular", font_size=35,)


painting_txt = (
    CompositeVideoClip([painting, txt.with_position((300, 475))])
    .add_mask()
    .with_duration(3)
    .crossfadein(0.5)
    .crossfadeout(0.5)
)

# FADEIN/FADEOUT EFFECT ON THE PAINTED IMAGE

painting_fading = CompositeVideoClip([im_freeze, painting_txt])

# FINAL CLIP AND RENDERING

final_clip = concatenate_videoclips([clip_before, painting_fading.with_duration(3), clip_after])

final_clip.write_videofile("media/audrey_edited.mp4", fps=test_video.fps, temp_audiofile="temp-audio.m4a",
                           remove_temp=True, codec="libx264", audio_codec="aac")
