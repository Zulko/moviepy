"""Contains everything that can help automate the cuts in MoviePy."""

from collections import defaultdict

import numpy as np

from moviepy.decorators import convert_parameter_to_seconds, use_clip_fps_by_default


@use_clip_fps_by_default
@convert_parameter_to_seconds(["start_time"])
def find_video_period(clip, fps=None, start_time=0.3):
    """Find the period of a video based on frames correlation.

    Parameters
    ----------

    clip : moviepy.Clip.Clip
      Clip for which the video period will be computed.

    fps : int, optional
      Number of frames per second used computing the period. Higher values will
      produce more accurate periods, but the execution time will be longer.

    start_time : float, optional
      First timeframe used to calculate the period of the clip.

    Examples
    --------

    >>> from moviepy.editor import *
    >>> from moviepy.video.tools.cuts import find_video_period
    >>>
    >>> clip = VideoFileClip("media/chaplin.mp4").subclip(0, 1).loop(2)
    >>> round(videotools.find_video_period(clip, fps=80), 6)
    1
    """

    def frame(t):
        return clip.get_frame(t).flatten()

    timings = np.arange(start_time, clip.duration, 1 / fps)[1:]
    ref = frame(0)
    corrs = [np.corrcoef(ref, frame(t))[0, 1] for t in timings]
    return timings[np.argmax(corrs)]


class FramesMatch:
    """Frames match inside a set of frames.

    Parameters
    ----------

    start_time : float
      Starting time.

    end_time : float
      End time.

    min_distance : float
      Lower bound on the distance between the first and last frames

    max_distance : float
      Upper bound on the distance between the first and last frames
    """

    def __init__(self, start_time, end_time, min_distance, max_distance):
        self.start_time = start_time
        self.end_time = end_time
        self.min_distance = min_distance
        self.max_distance = max_distance
        self.time_span = end_time - start_time

    def __str__(self):  # pragma: no cover
        return "(%.04f, %.04f, %.04f, %.04f)" % (
            self.start_time,
            self.end_time,
            self.min_distance,
            self.max_distance,
        )

    def __repr__(self):  # pragma: no cover
        return self.__str__()

    def __iter__(self):  # pragma: no cover
        return iter(
            (self.start_time, self.end_time, self.min_distance, self.max_distance)
        )

    def __eq__(self, other):
        return (
            other.start_time == self.start_time
            and other.end_time == self.end_time
            and other.min_distance == self.min_distance
            and other.max_distance == self.max_distance
        )


class FramesMatches(list):
    """Frames matches inside a set of frames.

    You can instantiate it passing a list of FramesMatch objects or
    using the class methods ``load`` and ``from_clip``.

    Parameters
    ----------

    lst : list
      Iterable of FramesMatch objects.
    """

    def __init__(self, lst):
        list.__init__(self, sorted(lst, key=lambda e: e.max_distance))

    def best(self, n=1, percent=None):
        """Returns a new instance of FramesMatches object or a FramesMatch
        from the current class instance given different conditions.

        By default returns the first FramesMatch that the current instance
        stores.

        Parameters
        ----------

        n : int, optional
          Number of matches to retrieve from the current FramesMatches object.
          Only has effect when ``percent=None``.

        percent : float, optional
          Percent of the current match to retrieve.

        Returns
        -------

        FramesMatch or FramesMatches : If the number of matches to retrieve is
          greater than 1 returns a FramesMatches object, otherwise a
          FramesMatch.

        """
        if percent is not None:
            n = len(self) * percent / 100
        return self[0] if n == 1 else FramesMatches(self[: int(n)])

    def filter(self, condition):
        """Return a FramesMatches object obtained by filtering out the
        FramesMatch which do not satistify a condition.

        Parameters
        ----------

        condition : func
          Function which takes a FrameMatch object as parameter and returns a
          bool.

        Examples
        --------
        >>> # Only keep the matches corresponding to (> 1 second) sequences.
        >>> new_matches = matches.filter( lambda match: match.time_span > 1)
        """
        return FramesMatches(filter(condition, self))

    def save(self, filename):
        """Save a FramesMatches object to a file.

        Parameters
        ----------

        filename : str
          Path to the file in which will be dumped the FramesMatches object data.
        """
        np.savetxt(
            filename,
            np.array([np.array(list(e)) for e in self]),
            fmt="%.03f",
            delimiter="\t",
        )

    @staticmethod
    def load(filename):
        """Load a FramesMatches object from a file.

        Parameters
        ----------

        filename : str
          Path to the file to use loading a FramesMatches object.

        Examples
        --------
        >>> matching_frames = FramesMatches.load("somefile")
        """
        arr = np.loadtxt(filename)
        mfs = [FramesMatch(*e) for e in arr]
        return FramesMatches(mfs)

    @staticmethod
    def from_clip(clip, distance_threshold, max_duration, fps=None, logger="bar"):
        """Finds all the frames that look alike in a clip, for instance to make
        a looping GIF.

        Parameters
        ----------

        clip : moviepy.video.VideoClip.VideoClip
          A MoviePy video clip.

        distance_threshold : float
          Distance above which a match is rejected.

        max_duration : float
          Maximal duration (in seconds) between two matching frames.

        fps : int, optional
          Frames per second (default will be ``clip.fps``).

        logger : str, optional
          Either ``"bar"`` for progress bar or ``None`` or any Proglog logger.

        Returns
        -------

        FramesMatches
            All pairs of frames with ``end_time - start_time < max_duration``
            and whose distance is under ``distance_threshold``.

        Examples
        --------

        We find all matching frames in a given video and turn the best match
        with a duration of 1.5 seconds or more into a GIF:

        >>> from moviepy import VideoFileClip
        >>> from moviepy.video.tools.cuts import FramesMatches
        >>>
        >>> clip = VideoFileClip("foo.mp4").resize(width=200)
        >>> matches = FramesMatches.from_clip(
        ...     clip, distance_threshold=10, max_duration=3,  # will take time
        ... )
        >>> best = matches.filter(lambda m: m.time_span > 1.5).best()
        >>> clip.subclip(best.start_time, best.end_time).write_gif("foo.gif")
        """
        N_pixels = clip.w * clip.h * 3

        def dot_product(F1, F2):
            return (F1 * F2).sum() / N_pixels

        frame_dict = {}  # will store the frames and their mutual distances

        def distance(t1, t2):
            uv = dot_product(frame_dict[t1]["frame"], frame_dict[t2]["frame"])
            u, v = frame_dict[t1]["|F|sq"], frame_dict[t2]["|F|sq"]
            return np.sqrt(u + v - 2 * uv)

        matching_frames = []  # the final result.

        for (t, frame) in clip.iter_frames(with_times=True, logger=logger):

            flat_frame = 1.0 * frame.flatten()
            F_norm_sq = dot_product(flat_frame, flat_frame)
            F_norm = np.sqrt(F_norm_sq)

            for t2 in list(frame_dict.keys()):
                # forget old frames, add 't' to the others frames
                # check for early rejections based on differing norms
                if (t - t2) > max_duration:
                    frame_dict.pop(t2)
                else:
                    frame_dict[t2][t] = {
                        "min": abs(frame_dict[t2]["|F|"] - F_norm),
                        "max": frame_dict[t2]["|F|"] + F_norm,
                    }
                    frame_dict[t2][t]["rejected"] = (
                        frame_dict[t2][t]["min"] > distance_threshold
                    )

            t_F = sorted(frame_dict.keys())

            frame_dict[t] = {"frame": flat_frame, "|F|sq": F_norm_sq, "|F|": F_norm}

            for i, t2 in enumerate(t_F):
                # Compare F(t) to all the previous frames

                if frame_dict[t2][t]["rejected"]:
                    continue

                dist = distance(t, t2)
                frame_dict[t2][t]["min"] = frame_dict[t2][t]["max"] = dist
                frame_dict[t2][t]["rejected"] = dist >= distance_threshold

                for t3 in t_F[i + 1 :]:
                    # For all the next times t3, use d(F(t), F(end_time)) to
                    # update the bounds on d(F(t), F(t3)). See if you can
                    # conclude on whether F(t) and F(t3) match.
                    t3t, t2t3 = frame_dict[t3][t], frame_dict[t2][t3]
                    t3t["max"] = min(t3t["max"], dist + t2t3["max"])
                    t3t["min"] = max(t3t["min"], dist - t2t3["max"], t2t3["min"] - dist)

                    if t3t["min"] > distance_threshold:
                        t3t["rejected"] = True

            # Store all the good matches (end_time,t)
            matching_frames += [
                (t1, t, frame_dict[t1][t]["min"], frame_dict[t1][t]["max"])
                for t1 in frame_dict
                if (t1 != t) and not frame_dict[t1][t]["rejected"]
            ]

        return FramesMatches([FramesMatch(*e) for e in matching_frames])

    def select_scenes(
        self, match_threshold, min_time_span, nomatch_threshold=None, time_distance=0
    ):
        """Select the scenes at which a video clip can be reproduced as the
        smoothest possible way, mainly oriented for the creation of GIF images.

        Parameters
        ----------

        match_threshold : float
          Maximum distance possible between frames. The smaller, the
          better-looping the GIFs are.

        min_time_span : float
          Minimum duration for a scene. Only matches with a duration longer
          than the value passed to this parameters will be extracted.

        nomatch_threshold : float, optional
          Minimum distance possible between frames. If is ``None``, then it is
          chosen equal to ``match_threshold``.

        time_distance : float, optional
          Minimum time offset possible between matches.

        Returns
        -------

        FramesMatches : New instance of the class with the selected scenes.

        Examples
        --------

        >>> from pprint import pprint
        >>> from moviepy.editor import *
        >>> from moviepy.video.tools.cuts import FramesMatches
        >>>
        >>> ch_clip = VideoFileClip("media/chaplin.mp4").subclip(1, 4)
        >>> clip = concatenate_videoclips([ch_clip.time_mirror(), ch_clip])
        >>>
        >>> result = FramesMatches.from_clip(clip, 10, 3).select_scenes(
        ...     1, 2, nomatch_threshold=0,
        ... )
        >>> pprint(result)
        [(1.0000, 4.0000, 0.0000, 0.0000),
         (1.1600, 3.8400, 0.0000, 0.0000),
         (1.2800, 3.7200, 0.0000, 0.0000),
         (1.4000, 3.6000, 0.0000, 0.0000)]
        """
        if nomatch_threshold is None:
            nomatch_threshold = match_threshold

        dict_starts = defaultdict(lambda: [])
        for (start, end, min_distance, max_distance) in self:
            dict_starts[start].append([end, min_distance, max_distance])

        starts_ends = sorted(dict_starts.items(), key=lambda k: k[0])

        result = []
        min_start = 0
        for start, ends_distances in starts_ends:

            if start < min_start:
                continue

            ends = [end for (end, min_distance, max_distance) in ends_distances]
            great_matches = [
                (end, min_distance, max_distance)
                for (end, min_distance, max_distance) in ends_distances
                if max_distance < match_threshold
            ]

            great_long_matches = [
                (end, min_distance, max_distance)
                for (end, min_distance, max_distance) in great_matches
                if (end - start) > min_time_span
            ]

            if not great_long_matches:
                continue  # No GIF can be made starting at this time

            poor_matches = {
                end
                for (end, min_distance, max_distance) in ends_distances
                if min_distance > nomatch_threshold
            }
            short_matches = {end for end in ends if (end - start) <= 0.6}

            if not poor_matches.intersection(short_matches):
                continue

            end = max(end for (end, min_distance, max_distance) in great_long_matches)
            end, min_distance, max_distance = next(
                e for e in great_long_matches if e[0] == end
            )

            result.append(FramesMatch(start, end, min_distance, max_distance))
            min_start = start + time_distance

        return FramesMatches(result)

    def write_gifs(self, clip, gifs_dir, **kwargs):
        """Extract the matching frames represented by the instance from a clip
        and write them as GIFs in a directory, one GIF for each matching frame.

        Parameters
        ----------

        clip : video.VideoClip.VideoClip
          A video clip whose frames scenes you want to obtain as GIF images.

        gif_dir : str
          Directory in which the GIF images will be written.

        kwargs
          Passed as ``clip.write_gif`` optional arguments.

        Examples
        --------

        >>> import os
        >>> from pprint import pprint
        >>> from moviepy.editor import *
        >>> from moviepy.video.tools.cuts import FramesMatches
        >>>
        >>> ch_clip = VideoFileClip("media/chaplin.mp4").subclip(1, 4)
        >>> clip = concatenate_videoclips([ch_clip.time_mirror(), ch_clip])
        >>>
        >>> result = FramesMatches.from_clip(clip, 10, 3).select_scenes(
        ...     1, 2, nomatch_threshold=0,
        ... )
        >>>
        >>> os.mkdir("foo")
        >>> result.write_gifs(clip, "foo")
        MoviePy - Building file foo/00000100_00000400.gif with imageio.
        MoviePy - Building file foo/00000115_00000384.gif with imageio.
        MoviePy - Building file foo/00000128_00000372.gif with imageio.
        MoviePy - Building file foo/00000140_00000360.gif with imageio.
        """
        for (start, end, _, _) in self:
            name = "%s/%08d_%08d.gif" % (gifs_dir, 100 * start, 100 * end)
            clip.subclip(start, end).write_gif(name, **kwargs)


@use_clip_fps_by_default
def detect_scenes(
    clip=None, luminosities=None, luminosity_threshold=10, logger="bar", fps=None
):
    """Detects scenes of a clip based on luminosity changes.

    Note that for large clip this may take some time.

    Returns
    -------

    tuple : cuts, luminosities
      cuts is a series of cuts [(0,t1), (t1,t2),...(...,tf)]
      luminosities are the luminosities computed for each
      frame of the clip.

    Parameters
    ----------

    clip : video.VideoClip.VideoClip, optional
      A video clip. Can be None if a list of luminosities is
      provided instead. If provided, the luminosity of each
      frame of the clip will be computed. If the clip has no
      'fps' attribute, you must provide it.

    luminosities : list, optional
      A list of luminosities, e.g. returned by detect_scenes
      in a previous run.

    luminosity_threshold : float, optional
      Determines a threshold above which the 'luminosity jumps'
      will be considered as scene changes. A scene change is defined
      as a change between 2 consecutive frames that is larger than
      (avg * thr) where avg is the average of the absolute changes
      between consecutive frames.

    logger : str, optional
      Either ``"bar"`` for progress bar or ``None`` or any Proglog logger.

    fps : int, optional
      Frames per second value. Must be provided if you provide
      no clip or a clip without fps attribute.
    """
    if luminosities is None:
        luminosities = [
            f.sum() for f in clip.iter_frames(fps=fps, dtype="uint32", logger=logger)
        ]

    luminosities = np.array(luminosities, dtype=float)
    if clip is not None:
        end = clip.duration
    else:
        end = len(luminosities) * (1.0 / fps)
    luminosity_diffs = abs(np.diff(luminosities))
    avg = luminosity_diffs.mean()
    luminosity_jumps = (
        1 + np.array(np.nonzero(luminosity_diffs > luminosity_threshold * avg))[0]
    )
    timings = [0] + list((1.0 / fps) * luminosity_jumps) + [end]
    cuts = [(t1, t2) for t1, t2 in zip(timings, timings[1:])]
    return cuts, luminosities
