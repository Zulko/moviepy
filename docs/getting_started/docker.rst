from moviepy.editor import *  

# Cargar imágenes  
imagenes = ["imagen1.jpg", "imagen2.jpg", "imagen3.jpg"]  
clips = [ImageClip(img).set_duration(5) for img in imagenes]  

# Agregar audio  
audio = AudioFileClip("audio.mp3")  
video = concatenate_videoclips(clips).set_audio(audio)  
video.write_videofile("video_final.mp4", fps=24)  
