"""Contains different functions to make end and opening credits, even though it is
difficult to fill everyone needs in this matter.
"""

from moviepy.decorators import convert_path_to_string
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.Resize import Resize
from moviepy.video.VideoClip import ImageClip, TextClip


class CreditsClip(TextClip):
    """Credits clip.

    Parameters
    ----------

    creditfile
      A string or path like object pointing to a text file
      whose content must be as follows: ::

        # This is a comment
        # The next line says : leave 4 blank lines
        .blank 4

        ..Executive Story Editor
        MARCEL DURAND

        ..Associate Producers
        MARTIN MARCEL
        DIDIER MARTIN

        ..Music Supervisor
        JEAN DIDIER


    width
      Total width of the credits text in pixels

    gap
      Horizontal gap in pixels between the jobs and the names

    color
      Color of the text. See ``TextClip.list('color')``
      for a list of acceptable names.

    font
      Name of the font to use. See ``TextClip.list('font')`` for
      the list of fonts you can use on your computer.

    font_size
      Size of font to use

    stroke_color
      Color of the stroke (=contour line) of the text. If ``None``,
      there will be no stroke.

    stroke_width
      Width of the stroke, in pixels. Can be a float, like 1.5.

    bg_color
      Color of the background. If ``None``, the background will be transparent.

    Returns
    -------

    image
      An ImageClip instance that looks like this and can be scrolled
      to make some credits: ::

          Executive Story Editor    MARCEL DURAND
             Associate Producers    MARTIN MARCEL
                                    DIDIER MARTIN
                Music Supervisor    JEAN DIDIER

    """

    @convert_path_to_string("creditfile")
    def __init__(
        self,
        creditfile,
        width,
        color="white",
        stroke_color="black",
        stroke_width=2,
        font="Impact-Normal",
        font_size=60,
        bg_color=None,
        gap=0,
    ):
        # Parse the .txt file
        texts = []
        one_line = True

        with open(creditfile) as file:
            for line in file:
                if line.startswith(("\n", "#")):
                    # exclude blank lines or comments
                    continue
                elif line.startswith(".blank"):
                    # ..blank n
                    for i in range(int(line.split(" ")[1])):
                        texts.append(["\n", "\n"])
                elif line.startswith(".."):
                    texts.append([line[2:], ""])
                    one_line = True
                elif one_line:
                    texts.append(["", line])
                    one_line = False
                else:
                    texts.append(["\n", line])

        left, right = ("".join(line) for line in zip(*texts))

        # Make two columns for the credits
        left, right = [
            TextClip(
                text=txt,
                color=color,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                font=font,
                font_size=font_size,
                text_align=align,
            )
            for txt, align in [(left, "left"), (right, "right")]
        ]

        both_columns = CompositeVideoClip(
            [left, right.with_position((left.w + gap, 0))],
            size=(left.w + right.w + gap, right.h),
            bg_color=bg_color,
        )

        # Scale to the required size
        scaled = both_columns.with_effects([Resize(width=width)])

        # Transform the CompositeVideoClip into an ImageClip

        # Calls ImageClip.__init__()
        super(TextClip, self).__init__(scaled.get_frame(0))
        self.mask = ImageClip(scaled.mask.get_frame(0), is_mask=True)
