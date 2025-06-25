from moviepy.editor import *
from moviepy.video.fx.all import fadein, fadeout

# === CONFIGURATION ===
video_size = (1080, 1920)
scene_duration = 4.2
fps = 30
audio_path = "ODNOGO_ULTRAFUNK_25s.wav"

# === Krishna images per scene ===
backgrounds = [
    "scene1_bg.jpg",
    "scene2_bg.jpg",
    "scene3_bg.jpg",
    "scene4_bg.jpg",
    "scene5_bg.jpg",
    "scene6_bg.jpg"
]

# === Corresponding PHONK Texts ===
texts = [
    "ॐ DIVINE SILENCE BEFORE CHAOS ॐ",
    "MAHA-YUDH MODE: ENGAGED",
    "▓▓▓▓▓▓▓▓\nPHONK ENERGY LEVEL: ∞\n▓▓▓▓▓▓▓▓",
    "YOU SEE A GOD. I SEE A COSMOS.",
    "ॐ VIBRATING WITH FREQUENCY OF LOVE ॐ",
    "DON’T MISTAKE CALM FOR WEAKNESS\nKRISHNA MODE: DEMON SLAYER ⚡"
]

fonts = [
    "Courier", "Impact", "Courier", "Arial", "Arial-Bold", "Arial-Black"
]

colors = [
    "cyan", "red", "white", "white", "pink", "red"
]

# === EFFECT FUNCTION (optional glitch flicker) ===
def flicker_effect(clip, rate=0.3, intensity=0.5):
    flashes = [
        clip.fx(vfx.lum_contrast, 0, 0, intensity).set_duration(0.05).set_start(i * rate)
        for i in range(int(clip.duration / rate))
    ]
    return CompositeVideoClip([clip] + flashes)

# === COMPILE SCENES ===
scene_clips = []

for i in range(6):
    # Background
    bg = ImageClip(backgrounds[i]).set_duration(scene_duration).resize(video_size)

    # Text
    txt = TextClip(texts[i],
                   fontsize=85,
                   font=fonts[i],
                   color=colors[i],
                   method="label").set_duration(scene_duration).set_position("center")

    txt = fadein(txt, 0.8).fadeout(0.5)
    txt = flicker_effect(txt)

    # Composite
    scene = CompositeVideoClip([bg, txt], size=video_size).set_duration(scene_duration)
    scene_clips.append(scene)

# === FINAL VIDEO ===
final = concatenate_videoclips(scene_clips, method="compose")

# Add audio
audio = AudioFileClip(audio_path)
final = final.set_audio(audio)

# Export
final.write_videofile("krishna_phonk_final_edit.mp4", fps=fps)
