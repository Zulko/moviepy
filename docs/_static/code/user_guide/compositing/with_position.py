"""让我们在视频上放置一些文字和图像。"""

from moviepy import TextClip, VideoFileClip, CompositeVideoClip, ImageClip

# 我们加载所有想要合成的剪辑
background = VideoFileClip("example2.mp4").subclipped(0, 2)
title = TextClip(
    "./example.ttf",
    text="Big Buck Bunny",
    font_size=80,
    color="#fff",
    text_align="center",
    duration=1,
)
author = TextClip(
    "./example.ttf",
    text="Blender Foundation",
    font_size=40,
    color="#fff",
    text_align="center",
    duration=1,
)
copyright = TextClip(
    "./example.ttf",
    text="© CC BY 3.0",
    font_size=20,
    color="#fff",
    text_align="center",
    duration=1,
)
logo = ImageClip("./example2.png", duration=1).resized(height=50)

# 我们希望标题水平居中，垂直方向从视频的 25% 处开始。我们可以设置为“中心”、“左”、“右”、“顶部”和“底部”，以及相对于剪辑大小的 %
title = title.with_position(("center", 0.25), relative=True)

# 我们希望作者位于中心，标题下方 30px 我们可以设置为像素
top = background.h * 0.25 + title.h + 30
left = (background.w - author.w) / 2
author = author.with_position((left, top))

# 我们希望版权信息位于底部 30px 处
copyright = copyright.with_position(("center", background.h - copyright.h - 30))

# 最后，我们希望徽标位于中心，但随着时间的推移而下降
# 我们可以通过将位置设置为以时间为参数的函数来实现，
# 很像 frame_function
top = (background.h - logo.h) / 2
# def t(t):
#     return ("center", top + t * 30)

logo = logo.with_position(lambda t: ("center", top + t * 30))

# We write the result
final_clip = CompositeVideoClip([background, title, logo, author, copyright])
final_clip.write_videofile("final_clip.mp4")
