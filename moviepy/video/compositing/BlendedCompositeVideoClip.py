from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

# Ensure that blend_modes is available, otherwise this cannot be used
try:
    from blend_modes import blend_modes
except ImportError as ex:
    msg = 'Using BlendedCompositeVideoClip requires the "blend_modes" package.'
    raise ImportError(msg)


class BlendedCompositeVideoClip(CompositeVideoClip):
    def __init__(self, *args, **kwargs):
        clips_blending = kwargs.pop('clips_blending', [])
        CompositeVideoClip.__init__(self, *args, **kwargs)

        # Sanitise and store each clip's blend kwargs
        self.clips_blending = self._check_clips_blending(clips_blending)

        # Custom definition of make_frame including blend_modes
        def make_frame(t):
            f = self.bg.get_frame(t)
            for (c, blend_kwargs) in self.playing_clips(t):
                f = c.blit_on(f, t, **blend_kwargs)
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
