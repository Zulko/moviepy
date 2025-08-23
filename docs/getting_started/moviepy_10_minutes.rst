"""
Rivane Story Movie 🎬
Full 11-scene generator with cartoon-style subtitles, narration, music, and Bogie’s bark.
"""

import os
import pyttsx3
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips,
    CompositeAudioClip, TextClip, CompositeVideoClip
)

# -------------------------------
# SETTINGS
# -------------------------------

PAGES = 11
PAGE_IMAGES = [f"page{i}.jpg" for i in range(1, PAGES+1)]
OUTPUT_FULL = "Rivane_Story.mp4"
OUTPUT_SCENES = True

MUSIC_FOLDER = "music"
BARK_FILE = "bark.mp3"

VOICE_RATE = 150
MUSIC_VOLUME = 0.2
ANIMATION_ZOOM = 1.2
FPS = 24
SCENE_DURATION = 15

SHOW_SUBTITLES = True
FONT_SIZE = 55
FONT_COLOR = "yellow"
STROKE_COLOR = "black"
STROKE_WIDTH = 3

# -------------------------------
# STORY TEXTS (11 pages)
# -------------------------------

SCENE_TEXTS = [
    """Narrator: Every morning, the sun peeked into Rivane’s room, just like a friendly hello.
Narrator: Rivane, a sweet three-year-old, loved getting ready for school.
Narrator: Her best friend, Bogie the dog, would wag his tail extra hard, ready for their morning adventure.""",

    """Mama Soukaina: "Good morning, my little sunshine!"
Narrator: Mama Soukaina gave Rivane a big hug.
Narrator: Rivane ate her breakfast quickly, excited to see her friends and learn new things.
Ritaj: "Have a wonderful day, Rivane!" """,

    """Narrator: With her backpack on, Rivane held Mama Soukaina’s hand, and Bogie trotted happily beside them.
Narrator: They walked past colorful houses and blooming flowers.
Narrator: Bogie always made sure Rivane was safe, like a fluffy guardian.""",

    """Narrator: As they neared the school gate, Rivane spotted something bright red on the sidewalk.
Rivane: "Look, Mama! What’s that?"
Mama Soukaina: "It looks like a balloon, Rivane. Maybe someone lost it." """,

    """Narrator: Rivane picked up the balloon and smiled.
Rivane: "Can I keep it, Mama?"
Mama Soukaina: "Of course, my love. Let’s take good care of it." """,

    """Narrator: At school, Rivane showed the balloon to her friends. Everyone laughed and played.
Narrator: Bogie barked happily, running in circles as if to join the fun.
Ritaj: "Be careful, Rivane! Don’t let it fly away!" """,

    """Narrator: Suddenly, a gust of wind lifted the balloon into the sky.
Rivane: "Oh no! My balloon!"
Narrator: Bogie barked loudly, chasing after it with determination.""",

    """Narrator: The balloon floated higher and higher.
Narrator: Rivane’s friends clapped and pointed.
Narrator: Even though the balloon was gone, Rivane felt happy to have shared the fun.""",

    """Narrator: Later that day, Mama Soukaina asked,
Mama Soukaina: "Did you enjoy your day, Rivane?"
Rivane: "Yes, Mama! And Bogie was the hero!" """,

    """Narrator: That night, Ritaj tucked Rivane into bed.
Ritaj: "Goodnight, Rivane. Sweet dreams."
Narrator: Bogie curled up at her feet, wagging his tail one last time.""",

    """Narrator: As Rivane closed her eyes, she whispered,
Rivane: "Thank you, Bogie. You’re my best friend forever."
Narrator: And with that, Rivane drifted into dreams, happy and safe.
The End."""
]

# -------------------------------
# FUNCTIONS
# -------------------------------

def generate_voice(text, filename):
    """Generate TTS narration with pyttsx3"""
    engine = pyttsx3.init()
    engine.setProperty("rate", VOICE_RATE)
    engine.save_to_file(text, filename)
    engine.runAndWait()
    return filename

def build_scene(image_file, text, music_file, scene_num):
    """Create one animated scene with narration, music, bark, and subtitles"""
    narration_file = f"narration_{scene_num}.mp3"
    generate_voice(text, narration_file)

    narration = AudioFileClip(narration_file)
    music = AudioFileClip(music_file).volumex(MUSIC_VOLUME).set_duration(SCENE_DURATION)
    bark = AudioFileClip(BARK_FILE).set_start(SCENE_DURATION/2).volumex(0.8)

    final_audio = CompositeAudioClip([narration, music, bark])

    # Animate image
    clip = ImageClip(image_file, duration=SCENE_DURATION)
    clip_zoom = clip.resize(ANIMATION_ZOOM).set_position("center")

    # Subtitles
    if SHOW_SUBTITLES:
        subtitle = TextClip(
            text, fontsize=FONT_SIZE, color=FONT_COLOR,
            stroke_color=STROKE_COLOR, stroke_width=STROKE_WIDTH,
            method="caption", size=(clip.w-100, None)
        ).set_position(("center", "bottom")).set_duration(SCENE_DURATION)
        clip_zoom = CompositeVideoClip([clip_zoom, subtitle])

    clip_final = clip_zoom.set_audio(final_audio)

    if OUTPUT_SCENES:
        clip_final.write_videofile(f"scene{scene_num}.mp4", fps=FPS, codec="libx264", audio_codec="aac")

    return clip_final

# -------------------------------
# MAIN
# -------------------------------

def main():
    print("🎬 Building Rivane Story Movie...")
    music_files = [os.path.join(MUSIC_FOLDER, m) for m in os.listdir(MUSIC_FOLDER) if m.endswith(".mp3")]
    if not music_files:
        raise FileNotFoundError("⚠️ No music files found in 'music' folder!")

    all_scenes = []
    for i, page in enumerate(PAGE_IMAGES, start=1):
        if i > len(SCENE_TEXTS):
            break
        print(f"Processing scene {i}...")
        music_file = music_files[(i-1) % len(music_files)]
        scene = build_scene(page, SCENE_TEXTS[i-1], music_file, i)
        all_scenes.append(scene)

    final = concatenate_videoclips(all_scenes)
    final.write_videofile(OUTPUT_FULL, fps=FPS, codec="libx264", audio_codec="aac")
    print("✅ Movie complete:", OUTPUT_FULL)

if __name__ == "__main__":
    main()
