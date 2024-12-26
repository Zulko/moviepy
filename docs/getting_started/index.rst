from moviepy.editor import *

# Define the text content for the video
header_text = "Carta de un cubano a Santa Claus: 'Tráeme esperanza'"
content_text = (
    "En medio de la crisis en Cuba, una carta dirigida a Santa Claus se viraliza por su mezcla de humor e ironía.\n\n"
    "\u201cTráeme un pedacito de esperanza, aquí hace más falta que un litro de aceite\u201d, escribe Christian Arbolaez.\n\n"
    "En su carta, pide desde alimentos hasta un cambio profundo en la realidad del país.\n\n"
    "A pesar de las dificultades, los cubanos mantienen el humor y la resiliencia.\n\n"
    "La vela que menciona simboliza tanto precariedad como fe en un futuro mejor."
)
closing_text = "La esperanza, el mejor regalo para Cuba.\n#LaChiringaCubana"

# Load images and define their durations
image1 = ImageClip("/path/to/image1.jpg").set_duration(5)  # Example image path
image2 = ImageClip("/path/to/image2.jpg").set_duration(5)
image3 = ImageClip("/path/to/image3.jpg").set_duration(5)

# Background music
background_music = AudioFileClip("/path/to/background_music.mp3").subclip(0, 80)

# Create text clips
header_clip = TextClip(header_text, fontsize=50, color="white", bg_color="black", size=(1080, 1920))
header_clip = header_clip.set_duration(5)

content_clip = TextClip(content_text, fontsize=35, color="white", bg_color="black", size=(1080, 1920))
content_clip = content_clip.set_duration(60).set_position('center')

closing_clip = TextClip(closing_text, fontsize=40, color="white", bg_color="black", size=(1080, 1920))
closing_clip = closing_clip.set_duration(15)

# Combine images and text
video = concatenate_videoclips([
    header_clip,
    image1.set_position("center"),
    content_clip,
    image2.set_position("center"),
    image3.set_position("center"),
    closing_clip
])

# Set audio
video = video.set_audio(background_music)

# Export video
video.write_videofile("carta_cubano_santa.mp4", fps=24)


