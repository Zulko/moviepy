"""All the visual effects that can be applied to VideoClip."""
# import every video fx function

from moviepy.video.fx.AccelDecel import AccelDecel
from moviepy.video.fx.BlackAndWhite import BlackAndWhite
from moviepy.video.fx.Blink import Blink
from moviepy.video.fx.Crop import Crop
from moviepy.video.fx.CrossFadeIn import CrossFadeIn
from moviepy.video.fx.CrossFadeOut import CrossFadeOut
from moviepy.video.fx.EvenSize import EvenSize
from moviepy.video.fx.FadeIn import FadeIn
from moviepy.video.fx.FadeOut import FadeOut
from moviepy.video.fx.Freeze import Freeze
from moviepy.video.fx.FreezeRegion import FreezeRegion
from moviepy.video.fx.GammaCorrection import GammaCorrection
from moviepy.video.fx.HeadBlur import HeadBlur
from moviepy.video.fx.InvertColors import InvertColors
from moviepy.video.fx.Loop import Loop
from moviepy.video.fx.LumContrast import LumContrast
from moviepy.video.fx.MakeLoopable import MakeLoopable
from moviepy.video.fx.Margin import Margin
from moviepy.video.fx.MaskColor import MaskColor
from moviepy.video.fx.MasksAnd import MasksAnd
from moviepy.video.fx.MasksOr import MasksOr
from moviepy.video.fx.MirrorX import MirrorX
from moviepy.video.fx.MirrorY import MirrorY
from moviepy.video.fx.MultiplyColor import MultiplyColor
from moviepy.video.fx.MultiplySpeed import MultiplySpeed
from moviepy.video.fx.Painting import Painting
from moviepy.video.fx.Resize import Resize
from moviepy.video.fx.Rotate import Rotate
from moviepy.video.fx.Scroll import Scroll
from moviepy.video.fx.SlideIn import SlideIn
from moviepy.video.fx.SlideOut import SlideOut
from moviepy.video.fx.SuperSample import SuperSample
from moviepy.video.fx.TimeMirror import TimeMirror
from moviepy.video.fx.TimeSymmetrize import TimeSymmetrize


__all__ = (
    "AccelDecel",
    "BlackAndWhite",
    "Blink",
    "Crop",
    "CrossFadeIn",
    "CrossFadeOut",
    "EvenSize",
    "FadeIn",
    "FadeOut",
    "Freeze",
    "FreezeRegion",
    "GammaCorrection",
    "HeadBlur",
    "InvertColors",
    "Loop",
    "LumContrast",
    "MakeLoopable",
    "Margin",
    "MasksAnd",
    "MaskColor",
    "MasksOr",
    "MirrorX",
    "MirrorY",
    "MultiplyColor",
    "MultiplySpeed",
    "Painting",
    "Resize",
    "Rotate",
    "Scroll",
    "SlideIn",
    "SlideOut",
    "SuperSample",
    "TimeMirror",
    "TimeSymmetrize",
)

if __name__ == '__main__':
    """
    1. 转场效果（Transitions）：
    
        淡入淡出（Fade In/Out）：
        这是最基本的转场效果之一，用于在两个视频片段之间平滑过渡。
        示例：视频开始时从黑色逐渐变亮（淡入），结束时逐渐变暗（淡出）。
        
        溶解（Dissolve）：
        将一个视频片段逐渐溶解到另一个片段中，产生混合效果。
        示例：两个场景之间的平滑过渡，常用于表示时间或地点的变化。
        
        擦除（Wipe）：
        一个视频片段以特定的方向擦除另一个片段，
        示例：从左到右、从上到下等方向的擦除效果。
    """
    from moviepy import VideoFileClip

    video = VideoFileClip("../../../media/video_with_failing_audio.mp4")
    fadein_effect = FadeIn(duration=2, initial_color=[255, 255, 0])
    video = fadein_effect.apply(video) # -> Clip

    video.preview()
    """
    2. 滤镜和色彩校正（Filters and Color Correction）：
        色彩滤镜（Color Filters）：
        改变视频的整体色调，例如复古、黑白、暖色调等。
        示例：应用一个棕褐色滤镜，使视频呈现出怀旧感。
        
        色彩校正（Color Correction）：
        调整视频的亮度、对比度、饱和度等，以改善视觉效果。
        示例：调整视频的亮度，使其在较暗的环境中更清晰。
    """

    """
    3. 视觉效果（Visual Effects）：

        模糊（Blur）：
        使视频的特定区域或整体变得模糊。
        示例：模糊视频背景，突出显示前景中的对象。
        锐化（Sharpen）：
        增强视频的细节和清晰度。
        示例：锐化视频，使其看起来更清晰。
        绿屏/色度键（Green Screen/Chroma Key）：
        移除视频中的特定颜色（通常是绿色），并用另一个视频或图像替换。
        示例：将人物从绿屏背景中提取出来，并放置在不同的场景中。
        叠加层（Overlays）：
        在视频上添加文本、图像或图形。
        示例：在视频中添加标题、字幕或logo。
        
    4. 速度效果（Speed Effects）：
        
        慢动作（Slow Motion）：
        降低视频的播放速度，使其看起来更慢。
        示例：放慢运动场景，突出显示细节。
        快进（Fast Forward）：
        提高视频的播放速度，使其看起来更快。
        示例：快进时间流逝的场景。
    """
    pass