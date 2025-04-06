from moviepy import VideoFileClip, CompositeVideoClip

# We load all the clips we want to compose
clip1 = VideoFileClip("example.mp4")
clip2 = VideoFileClip("example2.mp4").subclipped(0, 2)
clip3 = VideoFileClip("example3.mp4")

# 我们希望在 1 秒后停止 clip1
clip1 = clip1.with_end(1)

# 我们想在 1.5 秒后播放 clip2
clip2 = clip2.with_start(2)

# 我们想在 clip2 的结尾播放 clip3，所以只播放 3 秒
# 有时修改剪辑的持续时间比在其结尾处修改剪辑的持续时间更为实用
clip3 = clip3.with_start(clip2.end).with_duration(1)

# We write the result
final_clip = CompositeVideoClip([clip1, clip2, clip3])
final_clip.write_videofile("final_clip.mp4")
