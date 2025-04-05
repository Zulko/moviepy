"""Experimental module for subtitles support."""

import re

import numpy as np

from moviepy.decorators import convert_path_to_string
from moviepy.tools import convert_to_seconds
from moviepy.video.VideoClip import TextClip, VideoClip


class SubtitlesClip(VideoClip):
    """一个作为视频中“字幕轨道”的剪辑。
    这个类的一个特点是，字幕文本的图像不是预先生成的，而是在需要时才生成。

    示例
    --------
    .. code:: python
        from moviepy.video.tools.subtitles import SubtitlesClip
        from moviepy.video.io.VideoFileClip import VideoFileClip
        generator = lambda text: TextClip(text, font='./path/to/font.ttf', font_size=24, color='white')
        sub = SubtitlesClip("subtitles.srt", make_textclip=generator, encoding='utf-8')
        myvideo = VideoFileClip("myvideo.avi")
        final = CompositeVideoClip([clip, subtitles])
        final.write_videofile("final.mp4", fps=myvideo.fps)
    """

    def __init__(
            self,
            subtitles, # 可以是文件名（字符串或类似路径的对象），也可以是一个列表
            font=None, # 要使用的字体文件的路径。如果提供了 make_textclip，则为可选。
            make_textclip=None,
            # 用于生成文本剪辑的自定义函数。如果为 None，将生成一个 TextClip。
            # 该函数必须接受一个文本作为参数，并返回一个用作字幕的 VideoClip
            encoding=None
            # 可选，指定 srt 文件的编码。
            # 允许任何标准的 Python 编码（列在
            # https://docs.python.org/3.8/library/codecs.html#standard-encodings）
    ):
        VideoClip.__init__(self, has_constant_size=False)

        if not isinstance(subtitles, list):
            # `subtitles` is a string or path-like object
            subtitles = file_to_subtitles(subtitles, encoding=encoding)

        # subtitles = [(map(convert_to_seconds, times), text)
        #              for times, text in subtitles]
        self.subtitles = subtitles
        self.textclips = dict()

        self.font = font

        if make_textclip is None:
            if self.font is None:
                raise ValueError("Argument font is required if make_textclip is None.")

            def make_textclip(txt):
                return TextClip(
                    font=self.font,
                    text=txt,
                    font_size=24,
                    color="#ffffff",
                    stroke_color="#000000",
                    stroke_width=1,
                )

        self.make_textclip = make_textclip
        self.start = 0
        self.duration = max([tb for ((ta, tb), txt) in self.subtitles])
        self.end = self.duration

        def add_textclip_if_none(t):
            """Will generate a textclip if it hasn't been generated asked
            to generate it yet. If there is no subtitle to show at t, return
            false.
            """
            sub = [
                ((text_start, text_end), text)
                for ((text_start, text_end), text) in self.textclips.keys()
                if (text_start <= t < text_end)
            ]
            if not sub:
                sub = [
                    ((text_start, text_end), text)
                    for ((text_start, text_end), text) in self.subtitles
                    if (text_start <= t < text_end)
                ]
                if not sub:
                    return False
            sub = sub[0]
            if sub not in self.textclips.keys():
                self.textclips[sub] = self.make_textclip(sub[1])

            return sub

        def frame_function(t):
            sub = add_textclip_if_none(t)
            return self.textclips[sub].get_frame(t) if sub else np.array([[[0, 0, 0]]])

        def make_mask_frame(t):
            sub = add_textclip_if_none(t)
            return self.textclips[sub].mask.get_frame(t) if sub else np.array([[0]])

        self.frame_function = frame_function
        hasmask = bool(self.make_textclip("T").mask)
        self.mask = VideoClip(make_mask_frame, is_mask=True) if hasmask else None

    def in_subclip(self, start_time=None, end_time=None):
        """Returns a sequence of [(t1,t2), text] covering all the given subclip
        from start_time to end_time. The first and last times will be cropped so as
        to be exactly start_time and end_time if possible.
        """

        def is_in_subclip(t1, t2):
            try:
                return (start_time <= t1 < end_time) or (start_time < t2 <= end_time)
            except Exception:
                return False

        def try_cropping(t1, t2):
            try:
                return max(t1, start_time), min(t2, end_time)
            except Exception:
                return t1, t2

        return [
            (try_cropping(t1, t2), txt)
            for ((t1, t2), txt) in self.subtitles
            if is_in_subclip(t1, t2)
        ]

    def __iter__(self):
        return iter(self.subtitles)

    def __getitem__(self, k):
        return self.subtitles[k]

    def __str__(self):
        def to_srt(sub_element):
            (start_time, end_time), text = sub_element
            formatted_start_time = convert_to_seconds(start_time)
            formatted_end_time = convert_to_seconds(end_time)
            return "%s - %s\n%s" % (formatted_start_time, formatted_end_time, text)

        return "\n\n".join(to_srt(sub) for sub in self.subtitles)

    def match_expr(self, expr):
        """Matches a regular expression against the subtitles of the clip."""
        return SubtitlesClip(
            [sub for sub in self.subtitles if re.findall(expr, sub[1]) != []]
        )

    def write_srt(self, filename):
        """Writes an ``.srt`` file with the content of the clip."""
        with open(filename, "w+") as file:
            file.write(str(self))


@convert_path_to_string("filename")
def file_to_subtitles(filename, encoding=None):
    """Converts a srt file into subtitles.

    The returned list is of the form ``[((start_time,end_time),'some text'),...]``
    and can be fed to SubtitlesClip.

    Only works for '.srt' format for the moment.
    """
    times_texts = []
    current_times = None
    current_text = ""
    with open(filename, "r", encoding=encoding) as file:
        for line in file:
            times = re.findall("([0-9]*:[0-9]*:[0-9]*,[0-9]*)", line)
            if times:
                current_times = [convert_to_seconds(t) for t in times]
            elif line.strip() == "":
                times_texts.append((current_times, current_text.strip("\n")))
                current_times, current_text = None, ""
            elif current_times:
                current_text += line
    return times_texts
