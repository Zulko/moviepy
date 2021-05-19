from moviepy import *
from moviepy.video.tools.interpolators import Trajectory
from moviepy.video.tools.tracking import manual_tracking  # noqa 401


# LOAD THE CLIP (subclip 6'51 - 7'01 of a chaplin movie)
clip = VideoFileClip("media/chaplin.mp4")

# MANUAL TRACKING OF THE HEAD

# the next line is for the manual tracking and its saving
# to a file, it must be commented once the tracking has been done
# (after the first run of the script for instance).
# Note that we save the list (ti, xi, yi), not the functions fx and fy

# manual_tracking(clip, fps=6, savefile="blurred_trajectory.txt")


# IF THE MANUAL TRACKING HAS BEEN PREVIOUSLY DONE,
# LOAD THE TRACKING DATA AND CONVERT IT TO TRAJECTORY INTERPOLATORS fx(t), fy(t)

traj = Trajectory.from_file("blurred_trajectory.txt")


# BLUR CHAPLIN'S HEAD IN THE CLIP PASSING xi(t) and yi(t) FUNCTIONS

clip_blurred = clip.fx(vfx.headblur, traj.xi, traj.yi, 25)


# Generate the text, put in on a grey background

txt = TextClip(
    "Hey you! \n You're blurry!",
    color="grey70",
    size=clip.size,
    bg_color="grey20",
    font="Century-Schoolbook-Italic",
    font_size=40,
)


# Concatenate the Chaplin clip with the text clip, add audio

final = concatenate_videoclips([clip_blurred, txt.with_duration(3)]).with_audio(
    clip.audio
)

# We write the result to a file. Here we raise the bitrate so that
# the final video is not too ugly.

final.write_videofile("blurredChaplin.mp4")
