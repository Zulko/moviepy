"""实现 ImageSequenceClip，这是一个从一组图像文件创建视频剪辑的类。"""

import os

import numpy as np
from imageio.v2 import imread

from moviepy.video.VideoClip import VideoClip


class ImageSequenceClip(VideoClip):
    """
    由一系列图像组成的 VideoClip。
    """

    def __init__(
            self,
            sequence,
            #       可以是以下之一：
            #       - 文件夹的名称（仅包含图片）。图片将按字母数字顺序考虑。
            #       - 图像文件名称的列表。在这种情况下，您可以选择将图片加载到内存中。
            #       - 表示图像的 Numpy 数组的列表。在最后一种情况下，当前不支持遮罩。
            fps=None,  # 每秒读取的图片帧数。您可以提供每个图像的持续时间（使用 durations，见下文）代替。
            durations=None,  # 每个图片的持续时间列表。
            with_mask=True,  # 是否应将 PNG 图像的 alpha 层视为遮罩？
            is_mask=False,  # 此图片序列是否将用作动画遮罩。
            load_images=False,  # 指定应将所有图像加载到 RAM 中。如果您有少量将多次使用的图像，这将很有用。
    ):
        # CODE WRITTEN AS IT CAME, MAY BE IMPROVED IN THE FUTURE

        if (fps is None) and (durations is None):
            raise ValueError("Please provide either 'fps' or 'durations'.")
        VideoClip.__init__(self, is_mask=is_mask)

        # Parse the data

        fromfiles = True

        if isinstance(sequence, list):
            if isinstance(sequence[0], str):
                if load_images:
                    sequence = [imread(file) for file in sequence]
                    fromfiles = False
                else:
                    fromfiles = True
            else:
                # sequence is already a list of numpy arrays
                fromfiles = False
        else:
            # sequence is a folder name, make it a list of files:
            fromfiles = True
            sequence = sorted(
                [os.path.join(sequence, file) for file in os.listdir(sequence)]
            )

        # check that all the images are of the same size
        if isinstance(sequence[0], str):
            size = imread(sequence[0]).shape
        else:
            size = sequence[0].shape

        for image in sequence:
            image1 = image
            if isinstance(image, str):
                image1 = imread(image)
            if size != image1.shape:
                raise Exception(
                    "MoviePy: ImageSequenceClip requires all images to be the same size"
                )

        self.fps = fps
        if fps is not None:
            durations = [1.0 / fps for image in sequence]
            self.images_starts = [
                1.0 * i / fps - np.finfo(np.float32).eps for i in range(len(sequence))
            ]
        else:
            self.images_starts = [0] + list(np.cumsum(durations))
        self.durations = durations
        self.duration = sum(durations)
        self.end = self.duration
        self.sequence = sequence

        if fps is None:
            self.fps = len(sequence) / self.duration

        def find_image_index(t):
            return max(
                [i for i in range(len(self.sequence)) if self.images_starts[i] <= t]
            )

        if fromfiles:
            self.last_index = None
            self.last_image = None

            def frame_function(t):
                index = find_image_index(t)

                if index != self.last_index:
                    self.last_image = imread(self.sequence[index])[:, :, :3]
                    self.last_index = index

                return self.last_image

            if with_mask and (imread(self.sequence[0]).shape[2] == 4):
                self.mask = VideoClip(is_mask=True)
                self.mask.last_index = None
                self.mask.last_image = None

                def mask_frame_function(t):
                    index = find_image_index(t)
                    if index != self.mask.last_index:
                        frame = imread(self.sequence[index])[:, :, 3]
                        self.mask.last_image = frame.astype(float) / 255
                        self.mask.last_index = index

                    return self.mask.last_image

                self.mask.frame_function = mask_frame_function
                self.mask.size = mask_frame_function(0).shape[:2][::-1]

        else:

            def frame_function(t):
                index = find_image_index(t)
                return self.sequence[index][:, :, :3]

            if with_mask and (self.sequence[0].shape[2] == 4):
                self.mask = VideoClip(is_mask=True)

                def mask_frame_function(t):
                    index = find_image_index(t)
                    return 1.0 * self.sequence[index][:, :, 3] / 255

                self.mask.frame_function = mask_frame_function
                self.mask.size = mask_frame_function(0).shape[:2][::-1]

        self.frame_function = frame_function
        self.size = frame_function(0).shape[:2][::-1]
