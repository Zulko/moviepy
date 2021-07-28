"""Main video composition interface of MoviePy."""

import numpy as np
from PIL import Image

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.VideoClip import ColorClip, VideoClip


class CompositeVideoClip(VideoClip):
    """
    A VideoClip made of other videoclips displayed together. This is the
    base class for most compositions.

    Parameters
    ----------

    size
      The size (width, height) of the final clip.

    clips
      A list of videoclips.

      Clips with a higher ``layer`` attribute will be displayed
      on top of other clips in a lower layer.
      If two or more clips share the same ``layer``,
      then the one appearing latest in ``clips`` will be displayed
      on top (i.e. it has the higher layer).

      For each clip:

      - The attribute ``pos`` determines where the clip is placed.
          See ``VideoClip.set_pos``
      - The mask of the clip determines which parts are visible.

      Finally, if all the clips in the list have their ``duration``
      attribute set, then the duration of the composite video clip
      is computed automatically

    bg_color
      Color for the unmasked and unfilled regions. Set to None for these
      regions to be transparent (will be slower).

    use_bgclip
      Set to True if the first clip in the list should be used as the
      'background' on which all other clips are blitted. That first clip must
      have the same size as the final clip. If it has no transparency, the final
      clip will have no mask.

    The clip with the highest FPS will be the FPS of the composite clip.

    """

    def __init__(
        self, clips, size=None, bg_color=None, use_bgclip=False, is_mask=False
    ):

        if size is None:
            size = clips[0].size

        if use_bgclip and (clips[0].mask is None):
            transparent = False
        else:
            transparent = bg_color is None

        if bg_color is None:
            bg_color = 0.0 if is_mask else (0, 0, 0)

        fpss = [clip.fps for clip in clips if getattr(clip, "fps", None)]
        self.fps = max(fpss) if fpss else None

        VideoClip.__init__(self)

        self.size = size
        self.is_mask = is_mask
        self.clips = clips
        self.bg_color = bg_color

        if use_bgclip:
            self.bg = clips[0]
            self.clips = clips[1:]
            self.created_bg = False
        else:
            self.clips = clips
            self.bg = ColorClip(size, color=self.bg_color, is_mask=is_mask)
            self.created_bg = True

        # order self.clips by layer
        self.clips = sorted(self.clips, key=lambda clip: clip.layer)

        # compute duration
        ends = [clip.end for clip in self.clips]
        if None not in ends:
            duration = max(ends)
            self.duration = duration
            self.end = duration

        # compute audio
        audioclips = [v.audio for v in self.clips if v.audio is not None]
        if audioclips:
            self.audio = CompositeAudioClip(audioclips)

        # compute mask if necessary
        if transparent:
            maskclips = [
                (clip.mask if (clip.mask is not None) else clip.add_mask().mask)
                .with_position(clip.pos)
                .with_end(clip.end)
                .with_start(clip.start, change_end=False)
                .with_layer(clip.layer)
                for clip in self.clips
            ]

            self.mask = CompositeVideoClip(
                maskclips, self.size, is_mask=True, bg_color=0.0
            )

    def make_frame(self, t):
        """The clips playing at time `t` are blitted over one another."""
        frame = self.bg.get_frame(t).astype("uint8")
        im = Image.fromarray(frame)

        if self.bg.mask is not None:
            frame_mask = self.bg.mask.get_frame(t)
            im_mask = Image.fromarray(255 * frame_mask).convert("L")
            im = im.putalpha(im_mask)

        for clip in self.playing_clips(t):
            im = clip.blit_on(im, t)

        return np.array(im)

    def playing_clips(self, t=0):
        """Returns a list of the clips in the composite clips that are
        actually playing at the given time `t`.
        """
        return [clip for clip in self.clips if clip.is_playing(t)]

    def close(self):
        """Closes the instance, releasing all the resources."""
        if self.created_bg and self.bg:
            # Only close the background clip if it was locally created.
            # Otherwise, it remains the job of whoever created it.
            self.bg.close()
            self.bg = None
        if hasattr(self, "audio") and self.audio:
            self.audio.close()
            self.audio = None


def clips_array(array, rows_widths=None, cols_heights=None, bg_color=None):
    """Given a matrix whose rows are clips, creates a CompositeVideoClip where
    all clips are placed side by side horizontally for each clip in each row
    and one row on top of the other for each row. So given next matrix of clips
    with same size:

    ```python
    clips_array([[clip1, clip2, clip3], [clip4, clip5, clip6]])
    ```

    the result will be a CompositeVideoClip with a layout displayed like:

    ```
    ┏━━━━━━━┳━━━━━━━┳━━━━━━━┓
    ┃       ┃       ┃       ┃
    ┃ clip1 ┃ clip2 ┃ clip3 ┃
    ┃       ┃       ┃       ┃
    ┣━━━━━━━╋━━━━━━━╋━━━━━━━┫
    ┃       ┃       ┃       ┃
    ┃ clip4 ┃ clip5 ┃ clip6 ┃
    ┃       ┃       ┃       ┃
    ┗━━━━━━━┻━━━━━━━┻━━━━━━━┛
    ```

    If some clips doesn't fulfill the space required by the rows or columns
    in which are placed, that space will be filled by the color defined in
    ``bg_color``.

    array
      Matrix of clips included in the returned composited video clip.

    rows_widths
      Widths of the different rows in pixels. If ``None``, is set automatically.

    cols_heights
      Heights of the different columns in pixels. If ``None``, is set automatically.

    bg_color
       Fill color for the masked and unfilled regions. Set to ``None`` for these
       regions to be transparent (processing will be slower).
    """
    array = np.array(array)
    sizes_array = np.array([[clip.size for clip in line] for line in array])

    # find row width and col_widths automatically if not provided
    if rows_widths is None:
        rows_widths = sizes_array[:, :, 1].max(axis=1)
    if cols_heights is None:
        cols_heights = sizes_array[:, :, 0].max(axis=0)

    # compute start positions of X for rows and Y for columns
    xs = np.cumsum([0] + list(cols_heights))
    ys = np.cumsum([0] + list(rows_widths))

    for j, (x, ch) in enumerate(zip(xs[:-1], cols_heights)):
        for i, (y, rw) in enumerate(zip(ys[:-1], rows_widths)):
            clip = array[i, j]
            w, h = clip.size
            # if clip not fulfill row width or column height
            if (w < ch) or (h < rw):
                clip = CompositeVideoClip(
                    [clip.with_position("center")], size=(ch, rw), bg_color=bg_color
                ).with_duration(clip.duration)

            array[i, j] = clip.with_position((x, y))

    return CompositeVideoClip(array.flatten(), size=(xs[-1], ys[-1]), bg_color=bg_color)
