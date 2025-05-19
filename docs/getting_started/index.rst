
from moviepy.editor import *
from moviepy.audio.fx.all import audio_fadein, audio_fadeout
import numpy as np

# Create basic pixel animation using color blocks (as placeholder for real pixel art)
# A real animation would need sprite frames; here we simulate a basic 10s scene

# Create a blank scene
w, h = 256, 144  # Small pixel-art resolution
fps = 12
duration = 10  # seconds

# Define colors
colors = {
    "bg": (10, 10, 30),
    "chest": (150, 100, 50),
    "metal": (200, 200, 200),
    "wood": (120, 70, 40),
    "brick": (160, 60, 60),
    "metal_mat": (100, 100, 110),
    "scar": (255, 215, 0),
}

# Frame generator
def make_frame(t):
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:] = colors["bg"]

    # Draw chest (opens at t > 2)
    chest_x = w // 2 - 20
    chest_y = h // 2
    if t < 2:
        img[chest_y:chest_y+10, chest_x:chest_x+40] = colors["chest"]
        img[chest_y+10:chest_y+15, chest_x:chest_x+40] = colors["metal"]
    else:
        # Opened lid
        img[chest_y-5:chest_y, chest_x:chest_x+40] = colors["chest"]
        img[chest_y+10:chest_y+15, chest_x:chest_x+40] = colors["metal"]

        # Eject resources (simulate rising blocks)
        if t > 2.5:
            y_offset = int((t - 2.5) * 15)
            img[chest_y - y_offset:chest_y - y_offset + 5, chest_x+5:chest_x+15] = colors["wood"]
        if t > 3.5:
            y_offset = int((t - 3.5) * 15)
            img[chest_y - y_offset:chest_y - y_offset + 5, chest_x+20:chest_x+30] = colors["brick"]
        if t > 4.5:
            y_offset = int((t - 4.5) * 15)
            img[chest_y - y_offset:chest_y - y_offset + 5, chest_x+10:chest_x+20] = colors["metal_mat"]
        if t > 5.5:
            y_offset = int((t - 5.5) * 10)
            img[chest_y - y_offset:chest_y - y_offset + 6, chest_x+12:chest_x+28] = colors["scar"]

    return img

# Create video clip
video = VideoClip(make_frame, duration=duration).set_fps(fps)

# Load sound effect (you can replace this with actual Fortnite sounds if available)
# For now, we'll use generated tone placeholders due to lack of real audio file access
tone = AudioClip(lambda t: 0.5 * np.sin(2 * np.pi * 440 * t), duration=2).volumex(0.3)
chest_open_sound = tone.audio_fadein(0.2).set_start(2)

# Final audio track
audio = CompositeAudioClip([chest_open_sound])
final_video = video.set_audio(audio)

# Write to file
output_path = "/mnt/data/fortnite_chest_pixelart.mp4"
final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
