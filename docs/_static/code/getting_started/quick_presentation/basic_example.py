# Import everything needed to edit video clips
from moviepy import *

# Load file example.mp4 and extract only the subclip from 00:00:10 to 00:00:20
clip = VideoFileClip("long_examples/example2.mp4").subclipped(10, 20)

# Reduce the audio volume to 80% of his original volume
clip = clip.with_volume_scaled(0.8)

# Generate a text clip. You can customize the font, color, etc.
txt_clip = TextClip(
    font="example.ttf", text="Big Buck Bunny", font_size=70, color="white"
)

# 假设您希望它在屏幕中央出现 10 秒
txt_clip = txt_clip.with_position("center").with_duration(10)

# 将文本片段叠加在第一个视频片段上
video = CompositeVideoClip([clip, txt_clip])

# 将结果写入文件（有很多选项可用！）
video.write_videofile("result.mp4")
