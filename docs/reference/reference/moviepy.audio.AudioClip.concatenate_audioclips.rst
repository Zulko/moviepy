from moviepy.editor import ImageClip, VideoFileClip, concatenate_videoclips

# Dosya adlarını kendi dosyalarınızla uyarlayın
oflu_image_path = "oflu.jpg"          # Oflu görselinizin dosya adı
seytan_image_path = "seytan.jpg"        # Şeytan görselinizin dosya adı
voiceover_video_path = "seslendirme.mp4"  # Seslendirme içeren videonuzun dosya adı

# Görsellerin sürelerini ayarla (örneğin, her biri 2.5 saniye)
image_duration = 2.5

# Görsel klipler oluşturuluyor
oflu_clip = ImageClip(oflu_image_path).set_duration(image_duration)
seytan_clip = ImageClip(seytan_image_path).set_duration(image_duration)

# Seslendirme içeren video dosyasından ses parçasını alıyoruz
voiceover_video = VideoFileClip(voiceover_video_path)
voiceover_audio = voiceover_video.audio

# Ses dosyasının toplam süresini alalım
total_duration = voiceover_audio.duration

# Ses süresine uygun şekilde görselleri sırayla dizelim.
clips = []
current_time = 0
# Görselleri sırayla, dönüşümlü olarak ekleyelim; örneğin Oflu, sonra Şeytan...
while current_time < total_duration:
    if int(current_time // image_duration) % 2 == 0:
        clips.append(oflu_clip)
    else:
        clips.append(seytan_clip)
    current_time += image_duration

# Klipleri birleştiriyoruz
final_clip = concatenate_videoclips(clips)

# Videoya seslendirmeyi ekliyoruz
final_video = final_clip.set_audio(voiceover_audio)

# Çıktı videosunu kaydediyoruz (örneğin, final_video.mp4)
final_video.write_videofile("final_video.mp4", fps=24)
