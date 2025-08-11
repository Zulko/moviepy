import math
from dataclasses import dataclass
from typing import Union

import cv2
import numpy as np

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class Rotate(Effect):
    """
    Rotates the specified clip by ``angle`` degrees (or radians) anticlockwise
    If the angle is not a multiple of 90 (degrees) or ``center``, ``translate``,
    and ``bg_color`` are not ``None``, there will be black borders.
    You can make them transparent with:

    >>> new_clip = clip.with_mask().rotate(72)

    Parameters
    ----------

    clip : VideoClip
    A video clip.

    angle : float
    Either a value or a function angle(t) representing the angle of rotation.

    unit : str, optional
    Unit of parameter `angle` (either "deg" for degrees or "rad" for radians).

    resample : str, optional
    An optional resampling filter. One of "nearest", "bilinear", or "bicubic".

    expand : bool, optional
    If true, expands the output image to make it large enough to hold the
    entire rotated image. If false or omitted, make the output image the same
    size as the input image.

    translate : tuple, optional
    An optional post-rotate translation (a 2-tuple).

    center : tuple, optional
    Optional center of rotation (a 2-tuple). Origin is the upper left corner.

    bg_color : tuple, optional
    An optional color for area outside the rotated image. Only has effect if
    ``expand`` is true.
    """

    angle: float
    unit: str = "deg"
    resample: str = "bicubic"
    expand: bool = True
    center: tuple = None
    translate: tuple = None
    bg_color: tuple = None

    def rotate_frame(
        self,
        frame: np.ndarray,
        angle: float,
        resample: int,
        expand: bool,
        center: Union[tuple, None],
        translate: Union[tuple, None],
        bg_color: Union[tuple, None],
    ) -> np.ndarray:
        """
        Rotate a single image or mask using OpenCV.

        Parameters
        ----------
        frame : np.ndarray
            HxWxC RGB image (dtype uint8) or HxW mask (any dtype).

        angle : float
            Counter-clockwise rotation angle in degrees.

        resample : int
            One of cv2.INTER_NEAREST, cv2.INTER_LINEAR, or cv2.INTER_CUBIC.
            For masks, you’ll typically want cv2.INTER_NEAREST.
            Default is cv2.INTER_CUBIC.

        expand : bool
            If True, expand the output canvas so the full rotated frame fits.
            If False, output size == input size (cropping corners). Default False.
            Expansion does not account for translation.

        center : tuple or None
            (cx, cy) rotation center in pixel coords. Defaults to image center.

        translate : tuple or None
            (dx, dy) post-rotation translation in pixels. Default (0, 0).

        bg_color : tuple, scalar, or None
            Fill color for areas outside the frame.
            If `frame` is HxWx3 RGB, bg_color=(R,G,B).
            If HxW mask, bg_color is a scalar. Default black.

        Returns
        -------
        rotated : np.ndarray
            The rotated (and possibly expanded) frame or mask.
        """
        h, w = frame.shape[:2]

        if bg_color is None:
            bg_color = (0, 0, 0) if len(frame.shape) == 3 else 0

        # compute center
        cx, cy = center if center is not None else (w / 2, h / 2)

        # rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D((cx, cy), angle, 1)

        # expand canvas
        if expand:
            cos = np.abs(rotation_matrix[0, 0])
            sin = np.abs(rotation_matrix[0, 1])

            # compute the new bounding dimensions of the image
            new_w = math.ceil((h * sin) + (w * cos))
            new_h = math.ceil((h * cos) + (w * sin))

            # adjust the rotation matrix to take into account translation
            rotation_matrix[0, 2] += int(new_w / 2) - cx
            rotation_matrix[1, 2] += int(new_h / 2) - cy

            out_size = (new_w, new_h)
        else:
            out_size = (w, h)

        # Rotate the image
        rotated = cv2.warpAffine(
            frame,
            rotation_matrix,
            out_size,
            flags=resample,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=bg_color,
        )

        # If translate is specified, apply it after rotation
        if translate is not None:
            translation_matrix = np.float32(
                [[1, 0, translate[0]], [0, 1, translate[1]]]
            )
            rotated = cv2.warpAffine(
                rotated,
                translation_matrix,
                (rotated.shape[1], rotated.shape[0]),
                flags=resample,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=bg_color,
            )

        return rotated

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        try:
            resample = {
                "nearest": cv2.INTER_NEAREST,
                "bilinear": cv2.INTER_LINEAR,
                "bicubic": cv2.INTER_CUBIC,
            }[self.resample]
        except KeyError:
            raise ValueError(
                "'resample' argument must be either 'bilinear', 'nearest' or 'bicubic'"
            )

        if hasattr(self.angle, "__call__"):
            get_angle = self.angle
        else:
            get_angle = lambda t: self.angle

        def filter(get_frame, t):
            angle = get_angle(t)
            im = get_frame(t)

            if self.unit == "rad":
                angle = math.degrees(angle)

            angle %= 360
            if not self.center and not self.translate and not self.bg_color:
                if (angle == 0) and self.expand:
                    return im
                if (angle == 90) and self.expand:
                    transpose = [1, 0] if len(im.shape) == 2 else [1, 0, 2]
                    return np.transpose(im, axes=transpose)[::-1]
                elif (angle == 270) and self.expand:
                    transpose = [1, 0] if len(im.shape) == 2 else [1, 0, 2]
                    return np.transpose(im, axes=transpose)[:, ::-1]
                elif (angle == 180) and self.expand:
                    return im[::-1, ::-1]

            return self.rotate_frame(
                im,
                angle,
                resample,
                self.expand,
                self.center,
                self.translate,
                self.bg_color,
            )

        return clip.transform(filter, apply_to=["mask"])
