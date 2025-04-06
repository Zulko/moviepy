"""让我们编写一个自定义效果，在剪辑的底部添加一个基本的进度条。"""
from dataclasses import dataclass

from moviepy import VideoClip, VideoFileClip, Effect, Clip
from moviepy.decorators import requires_duration


# 在这里你可以看到一个装饰器，它将验证我们的剪辑是否有持续时间
# MoviePy 提供了一些在编写自己的效果时可能会派上用场的功能
@requires_duration
def progress_bar(
        clip: VideoClip,
        color: tuple, # 颜色：条形图的颜色（RGB 元组）
        height: int = 10 # 条形图的高度（以像素为单位）。默认值 = 10
):
    """
    在剪辑底部添加进度条
    """

    # Because we have define the filter func inside our global effect,
    # it have access to global effect scope and can use clip from inside filter
    def filter(get_frame, t):
        progression = t / clip.duration
        bar_width = int(progression * clip.w)

        # Showing a progress bar is just replacing bottom pixels
        # on some part of our frame
        frame = get_frame(t).copy()
        frame[-height:, 0: bar_width] = color

        return frame

    return clip.transform(filter, apply_to="mask")


@dataclass
class ProgressBar(Effect):
    """
    为剪辑底部添加一个动态进度条（随着时间推进）。

    参数:
    - color: 进度条颜色 (RGB 元组)
    - height: 进度条高度（单位: 像素）
    """

    color: tuple = (0, 255, 0)
    height: int = 10

    def apply(self, clip: Clip) -> Clip:
        def filter(get_frame, t):
            progression = t / clip.duration
            bar_width = int(progression * clip.w)

            frame = get_frame(t).copy()
            frame[-self.height:, 0:bar_width] = self.color

            return frame

        return clip.transform(filter)


my_clip = VideoFileClip("example2.mp4")
my_clip = my_clip.with_effects([ProgressBar(color=(255, 0, 0))])
my_clip.write_videofile("final_clip.mp4")

