from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.crop import crop


def freeze_region(clip, t=0, region=None, outside_region=None, mask=None):
    """Freezes one region of the clip while the rest remains animated.

    You can choose one of three methods by providing either `region`,
    `outside_region`, or `mask`.

    Parameters
    ----------

    t
      Time at which to freeze the freezed region.

    region
      A tuple (x1, y1, x2, y2) defining the region of the screen (in pixels)
      which will be freezed. You can provide outside_region or mask instead.

    outside_region
      A tuple (x1, y1, x2, y2) defining the region of the screen (in pixels)
      which will be the only non-freezed region.

    mask
      If not None, will overlay a freezed version of the clip on the current clip,
      with the provided mask. In other words, the "visible" pixels in the mask
      indicate the freezed region in the final picture.

    """
    if region is not None:

        x1, y1, x2, y2 = region
        freeze = (
            clip.fx(crop, *region)
            .to_ImageClip(t=t)
            .with_duration(clip.duration)
            .with_position((x1, y1))
        )
        return CompositeVideoClip([clip, freeze])

    elif outside_region is not None:

        x1, y1, x2, y2 = outside_region
        animated_region = clip.fx(crop, *outside_region).with_position((x1, y1))
        freeze = clip.to_ImageClip(t=t).with_duration(clip.duration)
        return CompositeVideoClip([freeze, animated_region])

    elif mask is not None:
        freeze = clip.to_ImageClip(t=t).with_duration(clip.duration).with_mask(mask)
        return CompositeVideoClip([clip, freeze])
