# -*- coding: utf-8 -*-

"""
    Tool tests meant to be run with pytest.
    
    Demonstrates issue #596 exists. 
    
    Note: Platform dependent test. Will only fail on Windows > NT. """

from os import remove
from os.path import join
import subprocess as sp
import time
# from tempfile import NamedTemporaryFile
from .test_helper import TMP_DIR

from moviepy.video.compositing.CompositeVideoClip import clips_array
from moviepy.video.VideoClip import ColorClip
from moviepy.video.io.VideoFileClip import VideoFileClip
# import pytest


def test_failure_to_release_file():
    """ This isn't really a test, because it is expected to fail.
        It demonstrates that there *is* a problem with not releasing resources when running on 
        Windows.

        The real issue was that, as of movepy 0.2.3.2, there was no way around it.

        See test_resourcerelease.py to see how the close() methods provide a solution.
    """

    # Get the name of a temporary file we can use.
    local_video_filename = join(
        TMP_DIR, "test_release_of_file_%s.mp4" % int(time.time()))

    # Repeat this so we can see that the problems escalate:
    for i in range(5):

        # Create a random video file.
        red = ColorClip((256, 200), color=(255, 0, 0))
        green = ColorClip((256, 200), color=(0, 255, 0))
        blue = ColorClip((256, 200), color=(0, 0, 255))

        red.fps = green.fps = blue.fps = 30
        video = clips_array([[red, green, blue]]).set_duration(1)

        try:
            video.write_videofile(local_video_filename)

            # Open it up with VideoFileClip.
            clip = VideoFileClip(local_video_filename)

            # Normally a client would do processing here.

            # All finished, so delete the clipS.
            clip.close()
            video.close()
            del clip
            del video

        except IOError:
            print(
                "On Windows, this succeeds the first few times around the loop"
                " but eventually fails.")
            print("Need to shut down the process now. No more tests in"
                  "this file.")
            return

        try:
            # Now remove the temporary file.
            # This will fail on Windows if the file is still locked.

            # In particular, this raises an exception with PermissionError.
            # In  there was no way to avoid it.

            remove(local_video_filename)
            print("You are not running Windows, because that worked.")
        except OSError:  # More specifically, PermissionError in Python 3.
            print("Yes, on Windows this fails.")
