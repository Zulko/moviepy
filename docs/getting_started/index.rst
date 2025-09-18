
import moviepy.editor as mp
import os

# List of input files (make sure they're in the same folder as this script)
video_files = [f"{i}.mp4" for i in range(1, 11)]

# Load and downscale to 720p
clips = [mp.VideoFileClip(v).resize(height=720) for v in video_files]

# -------------------------------
# 1. CLEAN VERSION
# -------------------------------
clean_final = mp.concatenate_videoclips(clips, method="compose")
clean_final.write_videofile("merged_clean.mp4", codec="libx264", audio_codec="aac")


# -------------------------------
# 2. EDITED VERSION
# -------------------------------
# Add simple transitions (crossfade of 1 sec)
clips_with_transitions = [clips[0]]
for c in clips[1:]:
    clips_with_transitions.append(c.crossfadein(1))

edited_final = mp.concatenate_videoclips(clips_with_transitions, method="compose", padding=-1)

# Add background music (royalty free track or any MP3 you have)
if os.path.exists("music.mp3"):
    music = mp.AudioFileClip("music.mp3").volumex(0.3)  # lower volume
    final_audio = mp.CompositeAudioClip([edited_final.audio, music])
    edited_final = edited_final.set_audio(final_audio)

# Add title and outro text
title = mp.TextClip("My Video Compilation", fontsize=70, color="white", bg_color="black", size=edited_final.size)
title = title.set_duration(3)

outro = mp.TextClip("The End", fontsize=60, color="white", bg_color="black", size=edited_final.size)
outro = outro.set_duration(3)

final_with_text = mp.concatenate_videoclips([title, edited_final, outro], method="compose")

final_with_text.write_videofile("merged_edited.mp4", codec="libx264", audio_codec="aac")













.. _getting_started:

Getting started with MoviePy
------------------------------

This section explain everything you need to start editing with MoviePy. To go further, have a look at the :ref:`user_guide` and the :ref:`reference_manual`.


.. toctree::
   :maxdepth: 1

   install
   quick_presentation
   moviepy_10_minutes
   docker
   updating_to_v2
   FAQ

