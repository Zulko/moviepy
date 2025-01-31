"""Implements ImageSequenceClip, a class to create a video clip from a set
of image files.
"""

import os

import numpy as np
from imageio.v2 import imread

from moviepy.video.VideoClip import VideoClip


class ImageSequenceClip(VideoClip):
    """A VideoClip made from a series of images.

    Parameters
    ----------

    sequence
      Can be one of these:

      - The name of a folder (containing only pictures). The pictures
        will be considered in alphanumerical order.
      - A list of names of image files. In this case you can choose to
        load the pictures in memory pictures
      - A list of Numpy arrays representing images. In this last case,
        masks are not supported currently.

    fps
      Number of picture frames to read per second. Instead, you can provide
      the duration of each image with durations (see below)

    durations
      List of the duration of each picture.

    with_mask
      Should the alpha layer of PNG images be considered as a mask ?

    is_mask
      Will this sequence of pictures be used as an animated mask.

    load_images
      Specify that all images should be loaded into the RAM. This is only
      interesting if you have a small number of images that will be used
      more than once.
    """

    def __init__(
        self,
        sequence,
        fps=None,
        durations=None,
        with_mask=True,
        is_mask=False,
        load_images=False,
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
