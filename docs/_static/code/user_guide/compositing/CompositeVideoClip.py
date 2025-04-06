"""让我们将三个视频片段堆叠在一起
CompositeVideoClip."""

from moviepy import VideoFileClip, CompositeVideoClip

# We load all the clips we want to compose
clip1 = VideoFileClip("example.mp4")
clip2 = VideoFileClip("example2.mp4").subclipped(0, 1)
clip3 = VideoFileClip("example3.mp4")

# 我们将它们连接起来，并将主题堆叠在一起，clip3 覆盖 clip2 覆盖 clip1
final_clip = CompositeVideoClip([clip1, clip2, clip3])
final_clip.write_videofile("final_clip.mp4")
