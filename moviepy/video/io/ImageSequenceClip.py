"""Implements ImageSequenceClip, a class to create a video clip from a set
of image files.
"""

import os
from bisect import bisect_right

import numpy as np
from imageio.v2 import imread

from moviepy.video.VideoClip import VideoClip


def _as_numpy_if_cuda_array(arr):
    if arr is None or not hasattr(arr, "__cuda_array_interface__"):
        return arr
    try:
        import cupy as cp

        return cp.asnumpy(arr)
    except Exception:
        return arr


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
      - A list of Numpy arrays representing images.

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

        self.fromfiles = True

        def _imread(filename):
            """Read an image from disk.

            Prefer OpenCV for formats where it is very unlikely to change
            semantics (notably PNG/BMP) and fall back to imageio otherwise.
            """
            ext = os.path.splitext(filename)[1].lower()

            # Allow users to disable OpenCV decoding if needed.
            if os.getenv("MOVIEPY_DISABLE_OPENCV"):
                return imread(filename)

            # OpenCV does not apply EXIF orientation in general, so keep
            # the default imageio/Pillow path for JPEGs and other formats
            # where EXIF orientation is common.
            if ext not in {".png", ".bmp"}:
                return imread(filename)

            try:
                import cv2

                arr = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
                if arr is None:
                    return imread(filename)

                if arr.ndim == 3 and arr.shape[2] == 3:
                    # BGR -> RGB
                    arr = np.ascontiguousarray(arr[:, :, ::-1])
                elif arr.ndim == 3 and arr.shape[2] == 4:
                    # BGRA -> RGBA
                    arr = np.ascontiguousarray(arr[:, :, [2, 1, 0, 3]])

                return arr
            except Exception:
                return imread(filename)

        self._imread = _imread

        if isinstance(sequence, list):
            if isinstance(sequence[0], str):
                if load_images:
                    sequence = [self._imread(file) for file in sequence]
                    self.fromfiles = False
            else:
                # sequence is already a list of numpy arrays
                self.fromfiles = False
        else:
            # sequence is a folder name, make it a list of files:
            sequence = sorted(
                [os.path.join(sequence, file) for file in os.listdir(sequence)]
            )

        # check that all the images are of the same size
        if isinstance(sequence[0], str):
            first_image = self._imread(sequence[0])
            size = first_image.shape
        else:
            first_image = None
            size = sequence[0].shape

        for image in sequence:
            image1 = image
            if isinstance(image, str):
                if (first_image is not None) and (image == sequence[0]):
                    image1 = first_image
                else:
                    image1 = self._imread(image)
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

        if self.fromfiles:
            self.last_index = None
            self.last_image = None

            first_shape = size
            if with_mask and (len(first_shape) >= 3) and (first_shape[2] == 4):
                self.mask = ImageSequenceClip(
                    sequence=sequence,
                    fps=fps,
                    durations=durations,
                    with_mask=False,
                    is_mask=True,
                    load_images=load_images,
                )

        else:
            if with_mask and (self.sequence[0].shape[2] == 4):
                self.mask = ImageSequenceClip(
                    sequence=sequence,
                    fps=fps,
                    durations=durations,
                    with_mask=False,
                    is_mask=True,
                    load_images=load_images,
                )

        self.size = self.frame_function(0).shape[:2][::-1]

    def _find_image_index(self, t):
        # images_starts is monotonic increasing; binary search is faster than scanning.
        idx = bisect_right(self.images_starts, t) - 1
        if idx < 0:
            return 0
        last = len(self.sequence) - 1
        return idx if idx <= last else last

    def frame_function(self, t):
        """Retrieves the frame corresponding to the given time `t`.

        Depending on whether the frames are loaded from files or provided as
        an in-memory sequence, this function either reads the frame from disk
        or accesses it directly from the sequence.

        Parameters
        ----------

        t (float): The time (in seconds) for which the corresponding frame
            is to be retrieved.

        Returns
        -------

        numpy.ndarray: The image frame at the specified time. If `is_mask`
            is True, the alpha channel of the image is returned
            as a float array normalized to the range [0, 1].
            Otherwise, the RGB channels of the image are returned.

        """
        index = self._find_image_index(t)

        if self.fromfiles:
            if (index == self.last_index) and (self.last_image is not None):
                return self.last_image
            self.last_index = index

            if self.is_mask:
                self.last_image = (
                    self._imread(self.sequence[index])[:, :, 3].astype(float) / 255.0
                )
            else:
                self.last_image = self._imread(self.sequence[index])[:, :, :3]

            return self.last_image
        else:
            if self.is_mask:
                img = _as_numpy_if_cuda_array(self.sequence[index])
                return img[:, :, 3].astype(float) / 255.0
            else:
                img = _as_numpy_if_cuda_array(self.sequence[index])
                return img[:, :, :3]
