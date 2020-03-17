from moviepy.decorators import requires_duration
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.VideoClip import ImageClip


@requires_duration
def freeze(clip, t=0, freeze_duration=None, total_duration=None,
           padding_end=0):
    """ Momentarily freeze the clip at time t.

    Set `t='end'` to freeze the clip at the end (actually it will freeze on the
    frame at time clip.duration - padding_end seconds).
    With ``duration``you can specify the duration of the freeze.
    With ``total_duration`` you can specify the total duration of
    the clip and the freeze (i.e. the duration of the freeze is
    automatically calculated). One of them must be provided.
    """

    if t=='end':
        t = clip.duration - padding_end

    if freeze_duration is None:
        freeze_duration = total_duration - clip.duration

    before = [clip.subclip(0,t)] if (t!=0) else []
    freeze = [clip.to_ImageClip(t).set_duration(freeze_duration)]
    after = [clip.subclip(t)] if (t !=clip.duration) else []
    return concatenate_videoclips(before + freeze + after)
  