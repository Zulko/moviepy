"""我们将四个视频片段并列在 2x2 的网格中。"""

from moviepy import VideoFileClip, clips_array, vfx

# We will use the same clip and transform it in 3 ways
clip1 = VideoFileClip("example.mp4").with_effects([vfx.Margin(10)])  # 添加 10px 轮廓
clip2 = clip1.with_effects([vfx.MirrorX()])  # 水平翻转
clip3 = clip1.with_effects([vfx.MirrorY()])  # 垂直翻转

clip4 = clip1.resized(0.6)  # 缩小到原来的60%

# 最终剪辑的形式将取决于数组的形状
# 我们希望我们的剪辑是我们的4个视频，2x2，所以我们做了一个2x2的数组
array = [
    [clip1, clip2],
    [clip3, clip4],
]
final_clip = clips_array(array)
# 让我们调整最终剪辑的大小，使其具有480px的宽度
final_clip = final_clip.resized(width=480)

final_clip.write_videofile("final_clip.mp4")
