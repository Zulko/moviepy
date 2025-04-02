"""Implements VideoFileClip, a class for video clips creation using video files."""

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.decorators import convert_path_to_string
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from moviepy.video.VideoClip import VideoClip


class VideoFileClip(VideoClip):
    """
    这是一个源自电影文件的视频剪辑类。例如：
    ```python
    clip = VideoFileClip("myHolidays.mp4")
    clip.close()
    with VideoFileClip("myMaskVideo.avi") as clip2:
        pass  # 使用上下文管理器，自动调用 close() 方法
    ```

    ## **属性说明**
    - **`filename`**：
      - 原始视频文件的名称。
    - **`fps`**：
      - 视频文件的原始帧率（每秒帧数）。

    **其他更通用的属性，请参考 `Clip()` 和 `VideoClip()` 的文档。**
    ---

    ## **生命周期管理**
    - `VideoFileClip` **会创建子进程并锁定文件**。
    - 如果创建了该类的实例，必须调用 `close()` 方法，否则子进程和文件锁不会被释放，直到进程结束。
    - 如果对 `VideoFileClip` 进行了复制，并且在一个实例上调用了 `close()`，那么其他实例的某些方法可能会无法正常工作。
    """

    # @convert_path_to_string("filename") 的作用就是： ✅ 确保 filename 始终是字符串
    # ✅ 支持 pathlib.Path，但最终转成 str
    # ✅ 防止路径格式错误，提升兼容性
    @convert_path_to_string("filename")
    def __init__(
            self,
            filename,
            #  **`filename`**：
            #  - 视频文件的名称，可以是字符串或路径对象。
            #  - 支持所有 `ffmpeg` 兼容的格式，如 `.ogv`、`.mp4`、`.mpeg`、`.avi`、`.mov` 等。
            decode_file=False,
            # decode_file 似乎是一个未启用或备用参数，因为在 FFMPEG_VideoReader 里并没有实际使用它。
            # 可能是计划用于提前解码整个视频，但当前版本 moviepy 仍然是按需解码，即只解码当前请求的帧。
            has_mask=False,
            #      - **`has_mask`**：
            #      如果视频文件包含遮罩（mask），请将其设置为 `True`。
            #      大多数视频文件不会包含遮罩，但某些视频编码格式支持遮罩。例如，如果你有一个带遮罩的 MoviePy `VideoClip`，
            #      可以将其保存为带遮罩的视频文件（参见 `VideoClip.write_videofile` 了解更多细节）。
            audio=True,
            #         - **`audio`**：
            #           - 如果视频没有音频，或者你不需要加载音频，请设置为 `False`。
            audio_buffersize=200000,
            # 音频缓冲区大小，单位是 字节（bytes）。
            # 200000 这个默认值 ≈ 200 KB。
            # 影响 音频流的加载方式，数值越大，占用内存越多，但读取效率可能更高。
            # 适用于大文件或高比特率音频，如果缓冲区太小，可能导致音频卡顿。
            target_resolution=None,
            #         - **`target_resolution`**：
            #           - 设置为 `(期望宽度, 期望高度)`，让 `ffmpeg` 在读取视频帧时直接进行缩放。
            #           - 这样做比读取原始高分辨率视频再缩放更快。
            #           - 如果宽度或高度的其中一个为 `None`，则会保持原始视频的宽高比进行缩放。
            resize_algorithm="bicubic",
            #         - **`resize_algorithm`**：
            #           - 指定用于缩放的算法，默认为 `"bicubic"`。
            #           - 其他常见选项包括 `"bilinear"` 和 `"fast_bilinear"`。
            #           - 详细信息请参考 [FFmpeg Scaler](https://ffmpeg.org/ffmpeg-scaler.html)。
            audio_fps=44100,
            # 音频采样率（Hz），即每秒采样多少个数据点。
            # 44100 是 CD 级别的标准采样率，适用于大多数音频文件。
            # 如果视频中的音频采样率不同（如 48000Hz），MoviePy 可能会自动调整到 44100Hz。
            # 影响音质，如果降低（如 22050Hz），会降低文件大小，但音质也会下降。
            audio_nbytes=2,
            # 音频位深度（bit depth），决定每个音频样本的数据位数：
            # 1 字节（8-bit）：低质量
            # 2 字节（16-bit）：CD 标准（默认）
            # 4 字节（32-bit）：高精度（适用于专业音频）
            # 默认值 2（16-bit PCM），常见于 MP3、WAV 等格式。
            fps_source="fps",
            #        - **`fps_source`**：
            #           - 指定从视频元数据中提取的帧率值，默认为 `"fps"`。
            #           - 但如果发现提取的帧率不正确，可以将其设置为 `"tbr"` 以尝试获取正确的帧率。
            pixel_format=None,
            #         - **`pixel_format`**（可选）：
            #           - 指定要读取的视频的像素格式。
            #           - 默认使用 `"rgb24"`，但如果 `has_mask=True`，则默认使用 `"rgba"`。
            is_mask=False,
            #  - **`is_mask`**：
            #  - 如果此视频剪辑将用作遮罩，请设置为 `True`。
    ):
        VideoClip.__init__(self, is_mask=is_mask)

        # Make a reader
        if not pixel_format:
            pixel_format = "rgba" if has_mask else "rgb24"

        self.reader = FFMPEG_VideoReader(
            filename,
            decode_file=decode_file,
            pixel_format=pixel_format,
            target_resolution=target_resolution,
            resize_algo=resize_algorithm,
            fps_source=fps_source,
        )

        # Make some of the reader's attributes accessible from the clip
        self.duration = self.reader.duration
        self.end = self.reader.duration

        self.fps = self.reader.fps
        self.size = self.reader.size
        self.rotation = self.reader.rotation

        self.filename = filename

        if has_mask:
            self.frame_function = lambda t: self.reader.get_frame(t)[:, :, :3]

            def mask_frame_function(t):
                return self.reader.get_frame(t)[:, :, 3] / 255.0

            self.mask = VideoClip(
                is_mask=True, frame_function=mask_frame_function
            ).with_duration(self.duration)
            self.mask.fps = self.fps

        else:
            self.frame_function = lambda t: self.reader.get_frame(t)

        # Make a reader for the audio, if any.
        if audio and self.reader.infos["audio_found"]:
            self.audio = AudioFileClip(
                filename,
                buffersize=audio_buffersize,
                fps=audio_fps,
                nbytes=audio_nbytes,
            )

    def __deepcopy__(self, memo):
        """Implements ``copy.deepcopy(clip)`` behaviour as ``copy.copy(clip)``.

        VideoFileClip class instances can't be deeply copied because the locked Thread
        of ``proc`` isn't pickleable. Without this override, calls to
        ``copy.deepcopy(clip)`` would raise a ``TypeError``:

        ```
        TypeError: cannot pickle '_thread.lock' object
        ```
        """
        return self.__copy__()

    def close(self):
        """Close the internal reader."""
        if self.reader:
            self.reader.close()
            self.reader = None

        try:
            if self.audio:
                self.audio.close()
                self.audio = None
        except AttributeError:  # pragma: no cover
            pass


if __name__ == '__main__':
    video = VideoFileClip("../../../media/chaplin.mp4")
    print("duration", video.duration)
    print("start", video.start)
    print("end", video.end)
    print("memoize", video.memoize)
    print("memoized_t", video.memoized_t)
    print("memoized_frame", video.memoized_frame)
    print("is_mask", video.is_mask)
    print("frame_function", video.frame_function)

    # frame = video.get_frame(2.5)  # 获取视频在 2.5 秒时的帧（NumPy 数组）
    # print("frame ->", frame)

    # video = video.subclipped(5, 8)  # 截取 5 秒到 10 秒的部分
    # video = video.resized(new_size=(200, 400))  # 调整视频高度为 720p，宽度会按比例缩放
    # video = video.rotated(30, bg_color="green")  # 顺时针旋转 90 度

    # 使用 cropped 方法裁剪视频
    # 假设你想裁剪出左上角坐标为 (x1=100, y1=50) 和右下角坐标为 (x2=500, y2=350) 的区域
    # video = video.cropped(x1=100, y1=50, x2=500, y2=350, width=120, height=150, x_center=430, y_center=100)
    # # 你还可以通过指定宽度和高度来裁剪
    # # 假设你想从 (x1=200, y1=100) 开始裁剪，裁剪区域的宽度为 300， 高度为 200
    # cropped_clip_by_size = video.cropped(x1=200, y1=100, width=300, height=200)
    # # 保存裁剪后的视频
    # cropped_clip.write_videofile("cropped_video.mp4")
    # cropped_clip_by_size.write_videofile("cropped_video_by_size.mp4")
    #
    # # 将视频放置在红色背景上，背景的大小为 (1920, 1080)，位置居中
    # video = video.with_background_color(size=(1080, 1920), color=(0,255,0), opacity=0.5)
    # # 保存合成后的视频
    # new_clip.write_videofile("video_with_red_background.mp4", codec="libx264")
    #
    # # 保存视频在时间 5 秒时的帧，保存为 'frame_at_5sec.png'
    # video.save_frame("frame_at_5sec.png", t=5)
    # # 如果视频有遮罩，并且需要将遮罩也保存到图像中，可以设置 with_mask=True
    # video.save_frame("frame_with_mask.png", t=5, with_mask=True)

    # video = video.with_duration(3, True)
    # video = video.with_section_cut_out(start_time=4, end_time=7) # 假设原视频是 0s - 9s，此操作会删除 4s-7s，最终视频为：0s - 4s  +  7s - 9s
    # video = video.with_speed_scaled(factor=2, final_duration=3) # factor=2 表示播放速度是原来的2倍，时长变为原来的一半
    # video = video.with_volume_scaled(factor=1.5) # 将整个剪辑的音量提高 50%
    # video = video.with_volume_scaled(factor=2, start_time=3, end_time=7) # 示例：将剪辑的第 3 秒到第 7 秒之间的音量加倍

    # video.time_transform()
    # video.with_audio
    # video.audio
    # video.without_audio()

    # video = video.with_opacity(0.9)

    # , pos, relative=False
    video = video.with_position((45, 150)) # x=45, y=150

    video.preview(fps=10, audio=False)