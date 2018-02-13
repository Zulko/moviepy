# -*- coding: utf-8 -*-

"""
Result: https://www.youtube.com/watch?v=Qu7HJrsEYFg

This is how we can imagine knights dancing at the 15th century, based on a very
serious historical study here: https://www.youtube.com/watch?v=zvCvOC2VwDc

Here is what we do:

0- Get the video of a dancing knight, and a (Creative Commons) audio music file.
1- load the audio file and automatically find the tempo
2- load the video and automatically find a segment that loops well
3- extract this segment, slow it down so that it matches the audio tempo,
   and make it loop forever.
4- Symmetrize this segment so that we will get two knights instead of one
5- Add a title screen and some credits, write to a file.


This example has been originally edited in an IPython Notebook, which makes it
easy to preview and fine-tune each part of the editing.
"""

from moviepy.editor import *
from moviepy.video.tools.cuts import find_video_period
from moviepy.audio.tools.cuts import find_audio_period


# Next lines are for downloading the required videos from Youtube.
# To do this you must have youtube-dl installed, otherwise you will need to
# download the videos by hand and rename them, as follows:
#     https://www.youtube.com/watch?v=zvCvOC2VwDc => knights.mp4
#     https://www.youtube.com/watch?v=lkY3Ek9VPtg => frontier.mp4

import os
if not os.path.exists("knights.mp4"):
    os.system("youtube-dl zvCvOC2VwDc -o knights.mp4")
    os.system("youtube-dl lkY3Ek9VPtg -o frontier.mp4")
#==========


# LOAD, EDIT, ANALYZE THE AUDIO


audio = (AudioFileClip("frontier.mp4")
         .subclip((4,7), (4,18))
         .audio_fadein(1)
         .audio_fadeout(1))

audio_period = find_audio_period(audio)
print ('Analyzed the audio, found a period of %.02f seconds'%audio_period)


# LOAD, EDIT, ANALYZE THE VIDEO


clip = (VideoFileClip("./knights.mp4", audio=False)
        .subclip((1,24.15),(1,26))
        .crop(x1=332, x2=910, y2=686))

video_period = find_video_period(clip, tmin=.3)
print ('Analyzed the video, found a period of %.02f seconds'%video_period)

edited_right = (clip.subclip(0,video_period)
                .speedx(final_duration=2*audio_period)
                .fx(vfx.loop, duration=audio.duration)
                .subclip(.25))

edited_left = edited_right.fx(vfx.mirror_x)

dancing_knights = (clips_array([[edited_left, edited_right]])
                   .fadein(1).fadeout(1).set_audio(audio).subclip(.3))

# MAKE THE TITLE SCREEN


txt_title = (TextClip("15th century dancing\n(hypothetical)", fontsize=70,
               font="Century-Schoolbook-Roman", color="white")
             .margin(top=15, opacity=0)
             .set_position(("center","top")))

title = (CompositeVideoClip([dancing_knights.to_ImageClip(), txt_title])
         .fadein(.5)
         .set_duration(3.5))


# MAKE THE CREDITS SCREEN


txt_credits = """
CREDITS

Video excerpt: Le combat en armure au XVe siècle
By J. Donzé, D. Jaquet, T. Schmuziger,
Université de Genève, Musée National de Moyen Age

Music: "Frontier", by DOCTOR VOX
Under licence Creative Commons
https://www.youtube.com/user/DOCTORVOXofficial

Video editing © Zulko 2014
 Licence Creative Commons (CC BY 4.0)
Edited with MoviePy: http://zulko.github.io/moviepy/
"""

credits = (TextClip(txt_credits, color='white',
            font="Century-Schoolbook-Roman", fontsize=35, kerning=-2,
            interline=-1, bg_color='black', size=title.size)
          .set_duration(2.5)
          .fadein(.5)
          .fadeout(.5))


# ASSEMBLE EVERYTHING, WRITE TO FILE

final = concatenate_videoclips([title, dancing_knights, credits])

final.write_videofile("dancing_knights.mp4", fps=clip.fps,
                      audio_bitrate="1000k", bitrate="4000k")