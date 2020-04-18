from moviepy.editor import *

# The background will be used for the blending
bg = VideoFileClip("../media/video_for_blend_modes.mp4").set_duration(1.0)

# Generate some text layers to demonstrate the blending modes
text_kwargs = {"font": "Helvetica", "fontsize": 96, "color": "#bbbb11"}
t1 = (
    TextClip("SOFT BLEND", **text_kwargs)
    .set_duration(1.0)
    .set_position(("center", "top"))
)
t2 = (
    TextClip("HARD BLEND", **text_kwargs)
    .set_duration(1.0)
    .set_position(("center", "bottom"))
)

comp = BlendedCompositeVideoClip(
    [bg, t1, t2],
    # Any blending parameters that aren't supplied will revert to defaults
    clips_blending=[
        {"blend_mode": "normal"},
        {"blend_mode": "soft_light", "blend_opacity": 0.8},
        {"blend_mode": "hard_light", "blend_weight": 0.8},
    ],
)

comp.write_videofile("../../test_blended_composition.mp4")
