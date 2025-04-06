"""让我们连接（一个接一个地播放）三个视频片段."""

from moviepy import VideoFileClip, concatenate_videoclips

# We load all the clips we want to concatenate
clip1 = VideoFileClip("example.mp4")
clip2 = VideoFileClip("example2.mp4").subclipped(0, 1)
clip3 = VideoFileClip("example3.mp4")

# 我们将它们连接起来并写出结果
final_clip = concatenate_videoclips([clip1, clip2, clip3])
final_clip.write_videofile("final_clip.mp4")
