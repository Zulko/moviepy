""" This module contains everything that can help automatize
the cuts in MoviePy """

from collections import defaultdict

import numpy as np

from moviepy.decorators import use_clip_fps_by_default


@use_clip_fps_by_default
def find_video_period(clip, fps=None, start_time=0.3):
    """ Finds the period of a video based on frames correlation """

    def frame(t):
        return clip.get_frame(t).flatten()

    timings = np.arange(start_time, clip.duration, 1.0 / fps)[1:]
    ref = frame(0)
    corrs = [np.corrcoef(ref, frame(t))[0, 1] for t in timings]
    return timings[np.argmax(corrs)]


class FramesMatch:
    """

    Parameters
    -----------

    start_time
      Starting time

    end_time
      End time

    min_distance
      Lower bound on the distance between the first and last frames

    max_distance
      Upper bound on the distance between the first and last frames

    """

    def __init__(self, start_time, end_time, min_distance, max_distance):
        self.start_time = start_time
        self.end_time = end_time
        self.min_distance = min_distance
        self.max_distance = max_distance
        self.time_span = end_time - start_time

    def __str__(self):

        return "(%.04f, %.04f, %.04f, %.04f)" % (
            self.start_time,
            self.end_time,
            self.min_distance,
            self.max_distance,
        )

    def __repr__(self):
        return "(%.04f, %.04f, %.04f, %.04f)" % (
            self.start_time,
            self.end_time,
            self.min_distance,
            self.max_distance,
        )

    def __iter__(self):
        return iter(
            (self.start_time, self.end_time, self.min_distance, self.max_distance)
        )


class FramesMatches(list):
    def __init__(self, lst):
        list.__init__(self, sorted(lst, key=lambda e: e.max_distance))

    def best(self, n=1, percent=None):
        if percent is not None:
            n = len(self) * percent / 100
        return self[0] if n == 1 else FramesMatches(self[:n])

    def filter(self, condition):
        """
        Returns a FramesMatches object obtained by filtering out the FramesMatch
        which do not satistify the condition ``condition``. ``condition``
        is a function (FrameMatch -> bool).

        Examples
        ---------
        >>> # Only keep the matches corresponding to (> 1 second) sequences.
        >>> new_matches = matches.filter( lambda match: match.time_span > 1)
        """
        return FramesMatches(filter(condition, self))

    def save(self, filename):
        np.savetxt(
            filename,
            np.array([np.array(list(e)) for e in self]),
            fmt="%.03f",
            delimiter="\t",
        )

    @staticmethod
    def load(filename):
        """Loads a FramesMatches object from a file.
        >>> matching_frames = FramesMatches.load("somefile")
        """
        arr = np.loadtxt(filename)
        mfs = [FramesMatch(*e) for e in arr]
        return FramesMatches(mfs)

    @staticmethod
    def from_clip(clip, distance_threshold, max_duration, fps=None):
        """Finds all the frames tht look alike in a clip, for instance to make a
        looping gif.

        This teturns a  FramesMatches object of the all pairs of frames with
        (end_time-start_time < max_duration) and whose distance is under
        distance_threshold.

        This is well optimized routine and quite fast.

        Examples
        ---------

        We find all matching frames in a given video and turn the best match with
        a duration of 1.5s or more into a GIF:

        >>> from moviepy import VideoFileClip
        >>> from moviepy.video.tools.cuts import FramesMatches
        >>> clip = VideoFileClip("foo.mp4").resize(width=200)
        >>> matches = FramesMatches.from_clip(clip, distance_threshold=10,
        ...                                   max_duration=3)  # will take time
        >>> best = matches.filter(lambda m: m.time_span > 1.5).best()
        >>> clip.subclip(best.start_time, best.end_time).write_gif("foo.gif")

        Parameters
        -----------

        clip
          A MoviePy video clip, possibly transformed/resized

        distance_threshold
          Distance above which a match is rejected

        max_duration
          Maximal duration (in seconds) between two matching frames

        fps
          Frames per second (default will be clip.fps)

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

        for (t, frame) in clip.iter_frames(with_times=True, logger="bar"):

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
                    # conclude on wether F(t) and F(t3) match.
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
        """

        match_threshold
          The smaller, the better-looping the gifs are.

        min_time_span
          Only GIFs with a duration longer than min_time_span (in seconds)
          will be extracted.

        nomatch_threshold
          If None, then it is chosen equal to match_threshold

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

    def write_gifs(self, clip, gif_dir):
        for (start, end, _, _) in self:
            name = "%s/%08d_%08d.gif" % (gif_dir, 100 * start, 100 * end)
            clip.subclip(start, end).write_gif(name)


@use_clip_fps_by_default
def detect_scenes(
    clip=None, luminosities=None, luminosity_threshold=10, logger="bar", fps=None
):
    """Detects scenes of a clip based on luminosity changes.

    Note that for large clip this may take some time

    Returns
    --------
    cuts, luminosities
      cuts is a series of cuts [(0,t1), (t1,t2),...(...,tf)]
      luminosities are the luminosities computed for each
      frame of the clip.

    Parameters
    -----------

    clip
      A video clip. Can be None if a list of luminosities is
      provided instead. If provided, the luminosity of each
      frame of the clip will be computed. If the clip has no
      'fps' attribute, you must provide it.

    luminosities
      A list of luminosities, e.g. returned by detect_scenes
      in a previous run.

    luminosity_threshold
      Determines a threshold above which the 'luminosity jumps'
      will be considered as scene changes. A scene change is defined
      as a change between 2 consecutive frames that is larger than
      (avg * thr) where avg is the average of the absolute changes
      between consecutive frames.

    logger
      Either "bar" for progress bar or None or any Proglog logger.

    fps
      Must be provided if you provide no clip or a clip without
      fps attribute.


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
