"""Experimental module for subtitles support."""

import re

import numpy as np

from moviepy.decorators import convert_path_to_string
from moviepy.tools import convert_to_seconds
from moviepy.video.VideoClip import TextClip, VideoClip


class SubtitlesClip(VideoClip):
    """A Clip that serves as "subtitle track" in videos.

    One particularity of this class is that the images of the subtitle texts
    are not generated beforehand, but only if needed.

    Parameters
    ----------

    subtitles : str or list
      Either the name of a subtitles file as a string or path-like object
      or a list.

    font : str, optional
      Name of the font to use. See ``TextClip.list("font")`` for the list of
      fonts you can use on your computer.

    font_size : int, optional
      Size of the font to use.

    color : str, optional
      Color of the text. See ``TextClip.list("color")`` for a list of
      acceptable names.

    stroke_color : str, optional
      Color of the stroke (contour line) of the text. If ``None``, there will
      be no stroke.

    stroke_width : float, optional
      Width of the stroke, in pixels. Can be a float, like ``1.5`` .

    auto_wrap : bool, optional
      Specifies if auto-wrapping of text is required (True or False).

    video_width : int, optional
      Compulsory parameter with ``auto_wrap`` to specify the width of the video
      (i.e. maximum text wrapping width).

    encoding : str, optional
      Optional, specifies srt file encoding.
      Any standard Python encoding is allowed (listed at
      https://docs.python.org/3.8/library/codecs.html#standard-encodings)


    Examples
    --------

    >>> from moviepy.video.tools.subtitles import SubtitlesClip
    >>> from moviepy.video.io.VideoFileClip import VideoFileClip
    >>>
    >>> sub = SubtitlesClip("subtitles.srt", auto_wrap=True, video_width=1280)
    >>> sub = SubtitlesClip("subtitles.srt", encoding="utf-8")
    >>>
    >>> myvideo = VideoFileClip("myvideo.avi")
    >>> final = CompositeVideoClip([clip, subtitles])
    >>> final.write_videofile("final.mp4", fps=myvideo.fps)

    """

    def __init__(
        self,
        subtitles,
        font="Arial",
        font_size=36,
        color="white",
        stroke_color="black",
        stroke_width=0.5,
        auto_wrap=None,
        video_width=None,
        encoding=None,
    ):

        VideoClip.__init__(self, has_constant_size=False)

        if not isinstance(subtitles, list):
            # `subtitles` is a string or path-like object
            subtitles = file_to_subtitles(subtitles, encoding=encoding)

        # subtitles = [(map(convert_to_seconds, times), text)
        #              for times, text in subtitles]
        self.subtitles = subtitles
        self.textclips = dict()

        make_textclip = None

        if auto_wrap:
            if not isinstance(video_width, int):
                raise ValueError(
                    "Valid video_width not specified for subtitle auto_wrap."
                )

            def make_textclip(txt):
                return TextClip(
                    txt,
                    font=font,
                    font_size=font_size,
                    color=color,
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                    method="pango",
                    size=(video_width, None),
                )

        else:

            def make_textclip(txt):
                return TextClip(
                    txt,
                    font=font,
                    font_size=font_size,
                    color=color,
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                    method="pango",
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

        def make_frame(t):
            sub = add_textclip_if_none(t)
            return self.textclips[sub].get_frame(t) if sub else np.array([[[0, 0, 0]]])

        def make_mask_frame(t):
            sub = add_textclip_if_none(t)
            return self.textclips[sub].mask.get_frame(t) if sub else np.array([[0]])

        self.make_frame = make_frame
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
        """Matchs a regular expression against the subtitles of the clip."""
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
        if current_times:
            times_texts.append((current_times, current_text.strip("\n")))
    return times_texts
