import numpy as np


# ------- CHECKING DEPENDENCIES -----------------------------------------
try:
    import cv2

    headblur_possible = True
    if cv2.__version__ >= "3.0.0":
        cv2.CV_AA = cv2.LINE_AA
except Exception:
    headblur_possible = False
# -----------------------------------------------------------------------


def headblur(clip, fx, fy, radius, intensity=None):
    """Returns a filter that will blur a moving part (a head ?) of the frames.

    The position of the blur at time t is defined by (fx(t), fy(t)), the radius
    of the blurring by ``radius`` and the intensity of the blurring by ``intensity``.

    Requires OpenCV for the circling and the blurring. Automatically deals with the
    case where part of the image goes offscreen.
    """
    if intensity is None:
        intensity = int(2 * radius / 3)

    def filter(gf, t):
        im = gf(t).copy()
        h, w, d = im.shape
        x, y = int(fx(t)), int(fy(t))
        x1, x2 = max(0, x - radius), min(x + radius, w)
        y1, y2 = max(0, y - radius), min(y + radius, h)
        region_size = y2 - y1, x2 - x1

        mask = np.zeros(region_size).astype("uint8")
        cv2.circle(mask, (radius, radius), radius, 255, -1, lineType=cv2.CV_AA)

        mask = np.dstack(3 * [(1.0 / 255) * mask])

        orig = im[y1:y2, x1:x2]
        blurred = cv2.blur(orig, (intensity, intensity))
        im[y1:y2, x1:x2] = mask * blurred + (1 - mask) * orig
        return im

    return clip.transform(filter)


# ------- OVERWRITE IF REQUIREMENTS NOT MET -----------------------------
if not headblur_possible:
    doc = headblur.__doc__

    def headblur(clip, fx, fy, r_zone, r_blur=None):
        """Fallback headblur FX function, used if OpenCV is not installed.

        This docstring will be replaced at runtime.
        """
        raise IOError("fx painting needs opencv")

    headblur.__doc__ = doc
# -----------------------------------------------------------------------
