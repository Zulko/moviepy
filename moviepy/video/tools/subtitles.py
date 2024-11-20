"""Experimental module for subtitles support."""

import re

import numpy as np

from moviepy.decorators import convert_path_to_string
from moviepy.tools import convert_to_seconds
from moviepy.video.VideoClip import TextClip, VideoClip


class SubtitlesClip(VideoClip):
    """A Clip that serves as "subtitle track" in videos.

    One particularity of this class is that the images of the
    subtitle texts are not generated beforehand, but only if
    needed.

    Parameters
    ----------

    subtitles
        Either the name of a file as a string or path-like object, or a list

    font
        Path to a font file to be used. Optional if make_textclip is provided.

    make_textclip
        A custom function to use for text clip generation. If None, a TextClip
        will be generated.

        The function must take a text as argument and return a VideoClip
        to be used as caption

    encoding
        Optional, specifies srt file encoding.
        Any standard Python encoding is allowed (listed at
        https://docs.python.org/3.8/library/codecs.html#standard-encodings)

    Examples
    --------

    >>> from moviepy.video.tools.subtitles import SubtitlesClip
    >>> from moviepy.video.io.VideoFileClip import VideoFileClip
    >>> generator = lambda text: TextClip(text, font='Georgia-Regular',
    ...                                   font_size=24, color='white')
    >>> sub = SubtitlesClip("subtitles.srt", generator)
    >>> sub = SubtitlesClip("subtitles.srt", generator, encoding='utf-8')
    >>> myvideo = VideoFileClip("myvideo.avi")
    >>> final = CompositeVideoClip([clip, subtitles])
    >>> final.write_videofile("final.mp4", fps=myvideo.fps)

    """

    def __init__(self, subtitles, font=None, make_textclip=None, encoding=None):
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
                    stroke_width=0.5,
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
