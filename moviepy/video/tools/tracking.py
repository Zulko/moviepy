"""
Contains different functions for tracking objects in videos, manually or automatically.
The tracking functions return results under the form:  ``( txy, (fx,fy) )`` where txy
is of the form [(ti, xi, yi)...] and (fx(t),fy(t)) give the position of the track for
all times t (if the time t is out of the time bounds of the tracking time interval fx
and fy return the position of the object at the start or at the end of the tracking time
interval).
"""

import numpy as np

from moviepy.decorators import convert_parameter_to_seconds, use_clip_fps_by_default
from moviepy.video.io.preview import imdisplay
from moviepy.video.tools.interpolators import Trajectory


try:
    import cv2

    autotracking_possible = True
except Exception:
    # Note: this will be later fixed with scipy/skimage replacements
    # but for the moment OpenCV is mandatory, so...
    autotracking_possible = False


@convert_parameter_to_seconds(["t1", "t2"])
@use_clip_fps_by_default
def manual_tracking(clip, t1=None, t2=None, fps=None, n_objects=1, savefile=None):
    """Manual tracking of objects in videoclips using the mouse.

    Allows manual tracking of an object(s) in the video clip between
    times `t1` and `t2`. This displays the clip frame by frame
    and you must click on the object(s) in each frame. If ``t2=None``
    only the frame at ``t1`` is taken into account.

    Returns a list ``[(t1, x1, y1), (t2, x2, y2)...]`` if there is one
    object per frame, else returns a list whose elements are of the
    form ``(ti, [(xi1, yi1), (xi2, yi2)...])``.


    Parameters
    ----------

    clip : video.VideoClip.VideoClip
      MoviePy video clip to track.

    t1 : float or str or tuple, optional
      Start time to to track (defaults is start of the clip). Can be expressed
      in seconds like ``15.35``, in ``(min, sec)``, in ``(hour, min, sec)``,
      or as a string: ``"01:03:05.35"``.

    t2 : float or str or tuple, optional
      End time to to track (defaults is end of the clip). Can be expressed
      in seconds like ``15.35``, in ``(min, sec)``, in ``(hour, min, sec)``,
      or as a string: ``"01:03:05.35"``.

    fps : int, optional
      Number of frames per second to freeze on. If None, the clip's
      fps attribute is used instead.

    n_objects : int, optional
      Number of objects to click on each frame.

    savefile : str, optional
      If provided, the result is saved to a file, which makes it easier to edit
      and re-use later.


    Examples
    --------

    >>> from moviepy import VideoFileClip
    >>> from moviepy.video.tools.tracking import manual_tracking
    >>>
    >>> clip = VideoFileClip("media/chaplin.mp4")
    >>>
    >>> # manually indicate 3 trajectories, save them to a file
    >>> trajectories = manual_tracking(clip, start_time=5, t2=7, fps=5,
    ...                                nobjects=3, savefile="track.text")
    >>>
    >>> # ...
    >>> # later, in another script, recover these trajectories
    >>> from moviepy.video.tools.tracking import Trajectory
    >>>
    >>> traj1, traj2, traj3 = Trajectory.load_list('track.text')
    >>>
    >>> # If ever you only have one object being tracked, recover it with
    >>> traj, =  Trajectory.load_list('track.text')
    """
    import pygame as pg

    screen = pg.display.set_mode(clip.size)
    step = 1.0 / fps
    if (t1 is None) and (t2 is None):
        t1, t2 = 0, clip.duration
    elif t2 is None:
        t2 = t1 + step / 2
    t = t1
    txy_list = []

    def gatherClicks(t):

        imdisplay(clip.get_frame(t), screen)
        objects_to_click = n_objects
        clicks = []
        while objects_to_click:

            for event in pg.event.get():

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_BACKSLASH:
                        return "return"
                    elif event.key == pg.K_ESCAPE:
                        raise KeyboardInterrupt()

                elif event.type == pg.MOUSEBUTTONDOWN:
                    x, y = pg.mouse.get_pos()
                    clicks.append((x, y))
                    objects_to_click -= 1

        return clicks

    while t < t2:

        clicks = gatherClicks(t)
        if clicks == "return":
            txy_list.pop()
            t -= step
        else:
            txy_list.append((t, clicks))
            t += step

    tt, xylist = zip(*txy_list)
    result = []
    for i in range(n_objects):
        xys = [e[i] for e in xylist]
        xx, yy = zip(*xys)
        result.append(Trajectory(tt, xx, yy))

    if savefile is not None:
        Trajectory.save_list(result, savefile)
    return result


def findAround(pic, pat, xy=None, r=None):
    """Find an image pattern in a picture optionally defining bounds to search.

    The image is found is ``pat`` is inside ``pic[x +/- r, y +/- r]``.

    Parameters
    ----------

    pic : numpy.ndarray
      Image where the pattern will be searched.

    pat : numpy.ndarray
      Pattern to search inside the image.

    xy : tuple or list, optional
      Position to search for the pattern. Use it in combination with ``radius``
      parameter to define the bounds of the search. If is ``None``, consider
      the whole picture.

    r : float, optional
      Radius used to define the bounds of the search when ``xy`` argument is
      defined.
    """
    if xy and r:
        h, w = pat.shape[:2]
        x, y = xy
        pic = pic[y - r : y + h + r, x - r : x + w + r]

    matches = cv2.matchTemplate(pat, pic, cv2.TM_CCOEFF_NORMED)
    yf, xf = np.unravel_index(matches.argmax(), matches.shape)
    return (x - r + xf, y - r + yf) if (xy and r) else (xf, yf)


def autoTrack(clip, pattern, tt=None, fps=None, radius=20, xy0=None):
    """Tracks a given pattern (small image array) in a video clip.

    Returns ``[(x1, y1), (x2, y2)...]`` where ``(xi, yi)`` are the coordinates
    of the pattern in the clip on frame ``i``. To select the frames you can
    either specify a list of times with ``tt`` or select a frame rate with
    ``fps``.

    This algorithm assumes that the pattern's aspect does not vary much and
    that the distance between two occurrences of the pattern in two consecutive
    frames is smaller than ``radius`` (if you set ``radius`` to -1 the pattern
    will be searched in the whole screen at each frame). You can also provide
    the original position of the pattern with xy0.

    Parameters
    ----------

    clip : video.VideoClip.VideoClip
      MoviePy video clip to track.

    pattern : numpy.ndarray
      Image to search inside the clip frames.

    tt : numpy.ndarray, optional
      Time frames used for auto tracking. As default is used the clip time
      frames according to its fps.

    fps : int, optional
      Overwrites fps value used computing time frames. As default, clip's fps.

    radius : int, optional
      Maximum radius to search looking for the pattern. Set to ``-1``,
      the pattern will be searched in the whole screen at each frame.

    xy0 : tuple or list, optional
      Original position of the pattern. If not provided, will be taken from the
      first tracked frame of the clip.
    """
    if not autotracking_possible:
        raise IOError(
            "Sorry, autotrack requires OpenCV for the moment. "
            "Install OpenCV (aka cv2) to use it."
        )

    if not xy0:
        xy0 = findAround(clip.get_frame(tt[0]), pattern)

    if tt is None:
        tt = np.arange(0, clip.duration, 1.0 / fps)

    xys = [xy0]
    for t in tt[1:]:
        xys.append(findAround(clip.get_frame(t), pattern, xy=xys[-1], r=radius))

    xx, yy = zip(*xys)

    return Trajectory(tt, xx, yy)
