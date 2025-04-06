"""Main video composition interface of MoviePy."""

from functools import reduce

import numpy as np
from PIL import Image

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.VideoClip import ColorClip, VideoClip


class CompositeVideoClip(VideoClip):
    """
    由其他视频剪辑组合而成的 VideoClip。这是大多数合成视频的基础类。
    具有最高 FPS 的剪辑将成为合成剪辑的 FPS。
    """

    def __init__(
            self,
            clips, # 一个视频剪辑列表。具有较高 ``layer`` 属性的剪辑将显示在具有较低 ``layer`` 属性的其他剪辑之上。
            #       如果两个或多个剪辑共享相同的 ``layer``，则列表中最后出现的剪辑将显示在顶部（即，它具有更高的图层）。
            #
            #       对于每个剪辑：
            #       - 属性 ``pos`` 确定剪辑的放置位置。
            #           请参阅 ``VideoClip.set_pos``
            #       - 剪辑的遮罩 (mask) 确定哪些部分是可见的。
            #
            #       最后，如果列表中的所有剪辑都设置了 ``duration`` 属性，
            #       则自动计算合成视频剪辑的持续时间。
            size=None, # 最终合成视频剪辑的尺寸 (宽度, 高度)。
            bg_color=None, #  未遮罩和未填充区域的颜色。如果这些区域需要透明，则设置为 None（速度会较慢）。
            use_bgclip=False, # 如果列表中的第一个剪辑应作为所有其他剪辑在其上进行绘制的“背景”，则设置为 True。
            # 第一个剪辑必须具有与最终剪辑相同的尺寸。如果它没有透明度，则最终剪辑将没有遮罩。
            is_mask=False
    ):
        if size is None:
            size = clips[0].size

        if use_bgclip and (clips[0].mask is None):
            transparent = False
        else:
            transparent = True if bg_color is None else False

        # If we must not use first clip as background and we dont have a color
        # we generate a black background if clip should not be transparent and
        # a transparent background if transparent
        if (not use_bgclip) and bg_color is None:
            if transparent:
                bg_color = 0.0 if is_mask else (0, 0, 0, 0)
            else:
                bg_color = 0.0 if is_mask else (0, 0, 0)

        fpss = [clip.fps for clip in clips if getattr(clip, "fps", None)]
        self.fps = max(fpss) if fpss else None

        VideoClip.__init__(self)

        self.size = size
        self.is_mask = is_mask
        self.clips = clips
        self.bg_color = bg_color

        # Use first clip as background if necessary, else use color
        # either set by user or previously generated
        if use_bgclip:
            self.bg = clips[0]
            self.clips = clips[1:]
            self.created_bg = False
        else:
            self.clips = clips
            self.bg = ColorClip(size, color=self.bg_color, is_mask=is_mask)
            self.created_bg = True

        # order self.clips by layer
        self.clips = sorted(self.clips, key=lambda clip: clip.layer_index)

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
                (clip.mask if (clip.mask is not None) else clip.with_mask().mask)
                .with_position(clip.pos)
                .with_end(clip.end)
                .with_start(clip.start, change_end=False)
                .with_layer_index(clip.layer_index)
                for clip in self.clips
            ]

            if use_bgclip and self.bg.mask:
                maskclips = [self.bg.mask] + maskclips

            self.mask = CompositeVideoClip(
                maskclips, self.size, is_mask=True, bg_color=0.0
            )

    def frame_function(self, t):
        """The clips playing at time `t` are blitted over one another."""
        # For the mask we recalculate the final transparency we'll need
        # to apply on the result image
        if self.is_mask:
            mask = np.zeros((self.size[1], self.size[0]), dtype=float)
            for clip in self.playing_clips(t):
                mask = clip.compose_mask(mask, t)

            return mask

        # Try doing clip merging with pillow
        bg_t = t - self.bg.start
        bg_frame = self.bg.get_frame(bg_t).astype("uint8")
        bg_img = Image.fromarray(bg_frame)

        if self.bg.mask:
            bgm_t = t - self.bg.mask.start
            bg_mask = (self.bg.mask.get_frame(bgm_t) * 255).astype("uint8")
            bg_mask_img = Image.fromarray(bg_mask).convert("L")

            # Resize bg_mask_img to match bg_img, always use top left corner
            if bg_mask_img.size != bg_img.size:
                mask_width, mask_height = bg_mask_img.size
                img_width, img_height = bg_img.size

                if mask_width > img_width or mask_height > img_height:
                    bg_mask_img = bg_mask_img.crop((0, 0, img_width, img_height))
                else:
                    new_mask = Image.new("L", (img_width, img_height), 0)
                    new_mask.paste(bg_mask_img, (0, 0))
                    bg_mask_img = new_mask

            bg_img = bg_img.convert("RGBA")
            bg_img.putalpha(bg_mask_img)

        # For each clip apply on top of current img
        current_img = bg_img
        for clip in self.playing_clips(t):
            current_img = clip.compose_on(current_img, t)

        # Turn Pillow image into a numpy array
        frame = np.array(current_img)

        # If frame have transparency, remove it
        # our mask will take care of it during rendering
        if frame.shape[2] == 4:
            return frame[:, :, :3]

        return frame

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


def concatenate_videoclips(
        clips, # 所有视频剪辑都必须设置其“持续时间”属性的列表。
        method="chain", # “链接”或“组成”：见上文。
        transition=None, # 将在列表的每两个剪辑之间播放的剪辑。
        bg_color=None, # 仅适用于 method='compose'。背景颜色。设置为 None 以获得透明剪辑
        is_mask=False,
        padding=0 # 仅适用于方法='compose'。两个连续剪辑的持续时间。请注意，对于负填充，剪辑将与其后面的剪辑同时部分播放
        # （对于淡入淡出的剪辑来说，负填充效果很棒）。非空填充会自动将方法设置为`compose`。
):
    """连接多个视频剪辑。返回由多个视频剪辑连接而成的视频剪辑。（连接意味着它们将一个接一个地播放）。

    有两种方法：
    - method="chain"：将生成一个剪辑，该剪辑仅输出连续剪辑的帧，如果它们的大小不同，则不进行任何校正。
    如果所有剪辑都没有蒙版，则生成的剪辑没有蒙版，否则蒙版是蒙版的连接（显然，对于没有蒙版的剪辑，使用完全不透明的蒙版）。

    如果您有不同大小的剪辑，并且想要将连接的结果直接写入文件，请改用方法“compose”。

    - method="compose"，如果剪辑的分辨率不同，则最终的分辨率将使得不需要调整任何剪辑的大小。
    因此，最终剪辑的高度与列表中最高的剪辑相同，宽度与列表中最宽的剪辑相同。所有尺寸较小的剪辑
    都将居中显示。如果 mask=True，边框将是透明的，否则将为“bg_color”指定的颜色。

    FPS 最高的剪辑将成为结果剪辑的 FPS。

    """
    if transition is not None:
        clip_transition_pairs = [[v, transition] for v in clips[:-1]]
        clips = reduce(lambda x, y: x + y, clip_transition_pairs) + [clips[-1]]
        transition = None

    timings = np.cumsum([0] + [clip.duration for clip in clips])

    sizes = [clip.size for clip in clips]

    w = max(size[0] for size in sizes)
    h = max(size[1] for size in sizes)

    timings = np.maximum(0, timings + padding * np.arange(len(timings)))
    timings[-1] -= padding  # Last element is the duration of the whole

    if method == "chain":
        def frame_function(t):
            i = max([i for i, e in enumerate(timings) if e <= t])
            return clips[i].get_frame(t - timings[i])

        def get_mask(clip):
            mask = clip.mask or ColorClip(clip.size, color=1, is_mask=True)
            if mask.duration is None:
                mask.duration = clip.duration
            return mask

        result = VideoClip(is_mask=is_mask, frame_function=frame_function)
        if any([clip.mask is not None for clip in clips]):
            masks = [get_mask(clip) for clip in clips]
            result.mask = concatenate_videoclips(masks, method="chain", is_mask=True)
            result.clips = clips
    elif method == "compose":
        result = CompositeVideoClip(
            [
                clip.with_start(t).with_position("center")
                for (clip, t) in zip(clips, timings)
            ],
            size=(w, h),
            bg_color=bg_color,
            is_mask=is_mask,
        )
    else:
        raise Exception(
            "MoviePy Error: The 'method' argument of "
            "concatenate_videoclips must be 'chain' or 'compose'"
        )

    result.timings = timings

    result.start_times = timings[:-1]
    result.start, result.duration, result.end = 0, timings[-1], timings[-1]

    audio_t = [
        (clip.audio, t) for clip, t in zip(clips, timings) if clip.audio is not None
    ]
    if audio_t:
        result.audio = CompositeAudioClip(
            [a.with_start(t) for a, t in audio_t]
        ).with_duration(result.duration)

    fpss = [clip.fps for clip in clips if getattr(clip, "fps", None) is not None]
    result.fps = max(fpss) if fpss else None
    return result
