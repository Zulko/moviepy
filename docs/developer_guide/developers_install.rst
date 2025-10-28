from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips

# Lista de imagens do Guarujá (substitua pelos caminhos reais)
imagens = [
    "enseada.jpg",
    "tombo.jpg",
    "pitangueiras.jpg",
    "por_do_sol.jpg"
]

# Textos correspondentes
textos = [
    "Vamos à praia…",
    "Sol, mar e tranquilidade te esperam.",
    "Deixe o cotidiano para trás e venha sentir.",
    "Partiu Guarujá!"
]

# Duração de cada cena em segundos
duracoes = [10, 20, 20, 10]  # total = 60s

# Lista de cores para cada legenda (estilo verão)
cores = ['#FFD700', '#00BFFF', '#FF6347', '#FF69B4']

clips = []

for img, txt, dur, cor in zip(imagens, textos, duracoes, cores):
    # Cria o clip de imagem
    clip_img = ImageClip(img).set_duration(dur).resize(height=1080).resize(width=1920)

    # Cria o clip de texto animado com deslizamento suave
    txt_clip = (TextClip(txt, fontsize=70, color=cor, font='Arial-Bold')
                .set_position(lambda t: ('center', 500 + 30*(1-t/dur)))  # desliza suavemente de cima para baixo
                .set_duration(dur)
                .crossfadein(1)
                .crossfadeout(1))

    # Combina imagem e texto
    clip = CompositeVideoClip([clip_img, txt_clip])
    clips.append(clip)

# Combina todos os clips em sequência
video = concatenate_videoclips(clips)

# Exporta o vídeo em 1080p
video.write_videofile("partiu_guaruja.mp4", fps=24)


