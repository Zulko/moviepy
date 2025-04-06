"""在此示例中，我们将连接两个剪辑，第二个剪辑的淡入淡出时长为 1 秒。"""

from moviepy import VideoFileClip, CompositeVideoClip, vfx

# 我们加载所有想要合成的剪辑
clip1 = VideoFileClip("example.mp4")
clip2 = VideoFileClip("example2.mp4")

clips = [
    clip1.with_end(2),
    clip2.with_start(1).with_effects([vfx.CrossFadeIn(1)]),
]
final_clip = CompositeVideoClip(clips)
final_clip.write_videofile("final_clip.mp4")
