import math

from moviepy import VideoFileClip, DataVideoClip, TextClip, CompositeVideoClip, ImageClip, ImageSequenceClip

# VideoClip



# VideoFileClip
video = VideoFileClip("../media/Study/IMG_6220.MOV")
print(video.duration)
print(video.fps)
video = video.resized((300,800))
# video = video.subclipped(8)
video = video.with_start(10)

# 设置 clip 在第 15 秒结束播放
new_clip = video.with_end(15)

# new_video = video.copy()
# new_video = new_video.time_transform(time_func=lambda t : t*2, apply_to=['mask', 'audio'])
# new_video = new_video.with_duration(video.duration * 2)
# video.preview(fps=20)
video.write_videofile("examples2.mov", codec="libx264")
# TextClip
video.close()
# new_video.close()
txt_clip1 = TextClip(
    text="Hello Word !",
    filename="../media/Study/test_clip_content.txt",

    method="label",
    font_size=10,

    size=(120, 120), # 区域
    margin=(0, 0),
    color="#FF0000",
    bg_color="black",

    stroke_color="green",
    stroke_width=0,

    text_align="left",
    horizontal_align="left",
    vertical_align="top",

    interline=4,
    transparent=False,
    duration=3,
)
# txt_clip1.preview()
# CompositeVideoClip
# final_clip = CompositeVideoClip(clips=[video, txt_clip1])
# final_clip.preview(fps=10)


# ImageSequenceClip
clip = ImageSequenceClip(
    "../media/doc_medias/example_img_dir",
    # durations=[1,1,1,1,1,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5],
    fps=10
)
# clip.preview()



# ImageClip
image = ImageClip(
    img="../media/pigs_in_a_polka.gif",
    # is_mask=True,
    # fromalpha=True,
    duration=3
)


# https://zulko.github.io/moviepy/user_guide/modifying.html
# 来修改剪辑的外观或计时
# 所有这些方法的工作原理都是将一个回调函数作为第一个参数，该函数将接收剪辑帧、时间点或两者，并返回修改后的版本。
# image.transform()
# image_transform

# 您可以使用time_transform(your_filter)更改剪辑的时间轴。其中your_filter是一个回调函数，以剪辑时间为参数并返回新的时间：
# 让我们把视频加速3倍
# def time_df(t):
#     print(t)
#     return t*2
#
# modified_clip1 = video.time_transform(lambda t: t)
# # 让我们用“正弦”时间扭曲效果来回播放视频
# # modified_clip2 = image.time_transform(lambda t: 1 + math.sin(t))
# print(type(modified_clip1))
# modified_clip1.preview()


# DataVideoClip




# UpdatedVideoClip


