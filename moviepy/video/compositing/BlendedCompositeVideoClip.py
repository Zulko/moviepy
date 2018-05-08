# Ensure that blend_modes is available, otherwise this cannot be used
try:
    from blend_modes import blend_modes
except ImportError as ex:
    msg = 'Using BlendedCompositeVideoClip requires the "blend_modes" package.' +\
        ' Please install with "pip install blend_modes" and try again.'
    raise ImportError(msg)

import types
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.tools.blending import blended_blit_on


class BlendedCompositeVideoClip(CompositeVideoClip):

    """

    A CompositeVideoClip made up of other VideoClips which can be composited
    together using blend modes.

    Parameters
    ----------
    (Inherited, see CompositeVideoClip)

    size
      The size (height x width) of the final clip.

    clips
      A list of videoclips. Each clip of the list will
      be displayed below the clips appearing after it in the list.
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

    (Specific to BlendedCompositeVideoClip)

    clips_blending
      A list of blending parameters corresponding to each of the VideoClips
      within the composition. If not supplied, or the length doesn't match
      the number of clips, then this will back to using the default MoviePy
      blit method, which corresponds to a "normal" blend mode.

      See moviepy.tools.blending.blended_blit for details on the blending
      parameters.

      Example list input format:
      [
        {
          'blend_mode': 'hard_light',
          'blend_opacity': 0.7,
          'blend_weight': 1.0
        },
        {
          'blend_mode': 'soft_light',
          'blend_opacity': 1.0,
          'blend_weight': 0.9
        },
        ...
      ]

    """

    def __init__(self, clips, size=None, bg_color=None, use_bgclip=False,
                 ismask=False, clips_blending=None):
        CompositeVideoClip.__init__(
            self, clips, size=size, bg_color=bg_color, use_bgclip=use_bgclip,
            ismask=ismask,
        )

        # Sanitise and store each clip's blend kwargs
        self.clips_blending = self._check_clips_blending(clips_blending)

        # Add in the blended_blit_on method to each of the VideoClips
        for c in self.clips:
            c.blended_blit_on = types.MethodType(blended_blit_on, c)

        # Custom definition of make_frame including blend_modes
        def make_frame(t):
            f = self.bg.get_frame(t)
            for (c, blend_kwargs) in self.playing_clips(t):
                f = c.blended_blit_on(f, t, **blend_kwargs)
            return f
        self.make_frame = make_frame
        return

    def playing_clips(self, t=0):
        playing = []
        for index, clip in enumerate(self.clips):
            if clip.is_playing(t):
                playing.append((clip, self.clips_blending[index]))
        return playing

    def _check_clips_blending(self, clips_blending):
        if clips_blending is None:
            clips_blending = []
        n_clips = len(self.clips)
        if len(clips_blending) != n_clips:
            clips_blending = [
                {
                    'blend_mode': 'normal',
                    'blend_opacity': 1.0,
                    'blend_weight': 1.0,
                } for i in range(n_clips)
            ]
        return clips_blending
