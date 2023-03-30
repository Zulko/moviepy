"""Utilities related with segmenting useful working with video clips."""

import numpy as np
import scipy.ndimage as ndi

from moviepy.video.VideoClip import ImageClip


def find_objects(clip, size_threshold=500, preview=False):
    """Returns a list of ImageClips representing each a separate object on
    the screen.

    Parameters
    ----------

    clip : video.VideoClip.ImageClip
      MoviePy video clip where the objects will be searched.

    size_threshold : float, optional
      Minimum size of what is considered an object. All objects found with
      ``size < size_threshold`` will be considered false positives and will
      be removed.

    preview : bool, optional
      Previews with matplotlib the different objects found in the image before
      applying the size threshold. Requires matplotlib installed.


    Examples
    --------

    >>> clip = ImageClip("media/afterimage.png")
    >>> objects = find_objects(clip)
    >>>
    >>> print(len(objects))
    >>> print([obj_.screenpos for obj_ in objects])
    """
    image = clip.get_frame(0)
    if not clip.mask:  # pragma: no cover
        clip = clip.add_mask()

    mask = clip.mask.get_frame(0)
    labelled, num_features = ndi.measurements.label(image[:, :, 0])

    # find the objects
    slices = []
    for obj in ndi.find_objects(labelled):
        if mask[obj[0], obj[1]].mean() <= 0.2:
            # remove letter holes (in o,e,a, etc.)
            continue
        if image[obj[0], obj[1]].size <= size_threshold:
            # remove very small slices
            continue
        slices.append(obj)
    indexed_slices = sorted(enumerate(slices), key=lambda slice: slice[1][1].start)

    letters = []
    for i, (sy, sx) in indexed_slices:
        # crop each letter separately
        sy = slice(sy.start - 1, sy.stop + 1)
        sx = slice(sx.start - 1, sx.stop + 1)
        letter = image[sy, sx]
        labletter = labelled[sy, sx]
        maskletter = (labletter == (i + 1)) * mask[sy, sx]
        letter = ImageClip(image[sy, sx])
        letter.mask = ImageClip(maskletter, is_mask=True)
        letter.screenpos = np.array((sx.start, sy.start))
        letters.append(letter)

    if preview:  # pragma: no cover
        import matplotlib.pyplot as plt

        print(f"Found {num_features} objects")
        fig, ax = plt.subplots(2)
        ax[0].axis("off")
        ax[0].imshow(labelled)
        ax[1].imshow([range(num_features)], interpolation="nearest")
        ax[1].set_yticks([])
        plt.show()

    return letters
