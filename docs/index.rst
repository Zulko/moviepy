from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

# === CONFIGURACIÓN ===
# Ruta a tu audio (el que me mandaste)
audio_path = "audio.ogg"   # cámbialo por el nombre real de tu archivo
# Lista de imágenes ilustrativas que usarás
imagenes = [
    "img1_intro.png",       # Diseño y Derecho
    "img2_rappi.png",       # Repartidor Rappi
    "img3_precios.png",     # Diferencia de precios
    "img4_ley1480.png",     # Estatuto consumidor
    "img5_reclamacion.png", # Reclamos
    "img6_repartidores.png",
    "img7_sentencia.png",
    "img8_ley2466.png",
    "img9_algoritmo.png",
    "img10_dinero.png",
    "img11_cierre.png"
]

# === CARGAR AUDIO ===
audio_clip = AudioFileClip(audio_path)
duracion_total = audio_clip.duration

# === ASIGNAR TIEMPO A CADA IMAGEN ===
# Divide el audio entre el número de imágenes
duracion_por_imagen = duracion_total / len(imagenes)

clips = []
for img in imagenes:
    clip = ImageClip(img).set_duration(duracion_por_imagen).resize(height=720)
    clips.append(clip)

# Concatenar las imágenes en secuencia
video = concatenate_videoclips(clips, method="compose")

# Añadir el audio al video
video = video.set_audio(audio_clip)

# Exportar el video final
video.write_videofile("video_final.mp4", fps=24)
