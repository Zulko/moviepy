from moviepy.editor import *
from moviepy.video.fx.all import rotate
import numpy as np

# Duration and FPS settings
duration = 8
fps = 24

# Create a black background clip (HD resolution)
background = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=duration)

# Gear Clip 1: A red gear using the unicode gear symbol "⚙"
gear1 = TextClip("⚙", fontsize=200, color="red", font="Arial-Bold", method="caption")
gear1 = gear1.set_duration(duration).set_position("center")
gear1 = gear1.fx(rotate, lambda t: 45 * t)  # rotates 45 degrees per second

# Gear Clip 2: A blue gear that is smaller and rotates in the opposite direction
gear2 = TextClip("⚙", fontsize=150, color="blue", font="Arial-Bold", method="caption")
gear2 = gear2.set_duration(duration).set_position((200, 200))
gear2 = gear2.fx(rotate, lambda t: -30 * t)  # rotates -30 degrees per second

# Title Text: "S63 VAG Spares" near the bottom of the video
title = TextClip("S63 VAG Spares", fontsize=70, color="white", font="Arial-Bold", method="caption")
title = title.set_duration(duration).set_position(("center", "bottom"))

# VW Badge: Simulated with text in a white box (top-left)
vw_badge = TextClip("VW", fontsize=50, color="black", font="Arial-Bold", method="caption", bg_color="white")
vw_badge = vw_badge.set_duration(duration).set_position((50, 50))

# Audi Badge: Simulated with text in a white box (top-right)
audi_badge = TextClip("AUDI", fontsize=50, color="black", font="Arial-Bold", method="caption", bg_color="white")
audi_badge = audi_badge.set_duration(duration).set_position((1080, 50))  # positioned near the right edge

# Create a composite clip layering all elements
final_clip = CompositeVideoClip([background, gear1, gear2, title, vw_badge, audi_badge])
final_clip = final_clip.set_duration(duration).set_fps(fps)

# Create a funky upbeat music placeholder using a combination of sine waves.
# (Replace this AudioClip with your own track if available.)
def funky_music(t):
    return 0.5 * (np.sin(2 * np.pi * 440 * t) + 0.3 * np.sin(2 * np.pi * 660 * t))
audio = AudioClip(funky_music, duration=duration, fps=44100).volumex(1.0)
final_clip = final_clip.set_audio(audio)

# Export the final video in .mov format with higher quality settings
output_path = "/mnt/data/S63VAGspares_YouTube_Intro_Modern.mov"
final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac',
                             bitrate="3000k", audio_bitrate="192k")
