from ..Clip import Clip
from ..decorators import outplace


class VideoClip(Clip):
    """Base class for video clips.

    See ``VideoFileClip``, ``ImageClip`` etc. for more user-friendly
    classes.


    Parameters
    -----------

    ismask
      `True` if the clip is going to be used as a mask.


    Attributes
    ----------

    size
      The size of the clip, (width,heigth), in pixels.

    w, h
      The width and height of the clip, in pixels.

    ismask
      Boolean set to `True` if the clip is a mask.

    make_frame
      A function ``t-> frame at time t`` where ``frame`` is a
      w*h*3 RGB array.

    mask (default None)
      VideoClip mask attached to this clip. If mask is ``None``,
                The video clip is fully opaque.

    audio (default None)
      An AudioClip instance containing the audio of the video clip.

    pos
      A function ``t->(x,y)`` where ``x,y`` is the position
      of the clip when it is composed with other clips.
      See ``VideoClip.set_pos`` for more details

    relative_pos
      See variable ``pos``.

    """

    def __init__(self, make_frame=None, ismask=False, duration=None,
                 has_constant_size=True):
        Clip.__init__(self)
        self.mask = None
        self.audio = None
        self.pos = lambda t: (0, 0)
        self.relative_pos = False
        if make_frame:
            self.make_frame = make_frame
            self.size = self.get_frame(0).shape[:2][::-1]
        self.ismask = ismask
        self.has_constant_size=has_constant_size
        if duration is not None:
            self.duration = duration
            self.end = duration

    @property
    def w(self):
        return self.size[0]

    @property
    def h(self):
        return self.size[1]

    @property
    def aspect_ratio(self):
        return self.w / float(self.h)

    # ----------------------------------------------------------------
    # Audio

    @outplace
    def without_audio(self):
        """Remove the clip's audio.

        Return a copy of the clip with audio set to None.

        """
        self.audio = None

