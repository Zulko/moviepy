import numpy as np


# ------- CHECKING DEPENDENCIES -----------------------------------------
painting_possible = True
try:
    from skimage.filter import sobel
except Exception:
    try:
        from scipy.ndimage.filters import sobel
    except Exception:
        painting_possible = False
# -----------------------------------------------------------------------


def to_painting(image, saturation=1.4, black=0.006):
    """Transforms any photo into some kind of painting."""
    edges = sobel(image.mean(axis=2))
    darkening = black * (255 * np.dstack(3 * [edges]))
    painting = saturation * image - darkening
    return np.maximum(0, np.minimum(255, painting)).astype("uint8")


def painting(clip, saturation=1.4, black=0.006):
    """
    Transforms any photo into some kind of painting. Saturation
    tells at which point the colors of the result should be
    flashy. ``black`` gives the amount of black lines wanted.
    Requires Scikit-image or Scipy installed.
    """
    return clip.image_transform(lambda im: to_painting(im, saturation, black))


# ------- OVERWRITE IF REQUIREMENTS NOT MET -----------------------------

if not painting_possible:
    doc = painting.__doc__

    def painting(clip, saturation=None, black=None):
        """Fallback painting FX function, used if scikit-image and scipy are not
        installed.

        This docstring will be replaced at runtime.
        """
        raise IOError("fx painting needs scikit-image or scipy")

    painting.__doc__ = doc
# -----------------------------------------------------------------------
