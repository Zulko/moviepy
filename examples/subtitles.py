from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy import TextClip, CompositeVideoClip, VideoFileClip


# generate custom textclips for the subtitles
generator = lambda text: TextClip(text=text, font="../media/doc_medias/example.ttf", font_size=24, color="white")
subtitles = SubtitlesClip("../media/subtitles.srt", make_textclip=generator, encoding="utf-8")

# video clip
clip = VideoFileClip("../media/chaplin.mp4")

final = CompositeVideoClip([clip, subtitles])
final.write_videofile("../../test_subtitles.mp4", fps=clip.fps)
