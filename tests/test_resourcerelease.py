# -*- coding: utf-8 -*-

"""
    Tool tests meant to be run with pytest.
    
    Testing whether issue #596 has been repaired. 
    
    Note: Platform dependent test. Will only fail on Windows > NT. """

from os import remove
from os.path import join
import subprocess as sp
import time
# from tempfile import NamedTemporaryFile
from test_helper import TMP_DIR

from moviepy.video.compositing.CompositeVideoClip import clips_array
from moviepy.video.VideoClip import ColorClip
from moviepy.video.io.VideoFileClip import VideoFileClip


def test_release_of_file_via_close():
    # Create a random video file.
    red = ColorClip((1024, 800), color=(255, 0, 0))
    green = ColorClip((1024, 800), color=(0, 255, 0))
    blue = ColorClip((1024, 800), color=(0, 0, 255))

    red.fps = green.fps = blue.fps = 30

    # Repeat this so we can see no conflicts.
    for i in range(5):
        # Get the name of a temporary file we can use.
        local_video_filename = join(TMP_DIR, "test_release_of_file_via_close_%s.mp4" % int(time.time()))

        with clips_array([[red, green, blue]]) as ca:
            video = ca.set_duration(1)

            video.write_videofile(local_video_filename)

        # Open it up with VideoFileClip.
        with VideoFileClip(local_video_filename) as clip:
            # Normally a client would do processing here.
            pass

        # Now remove the temporary file.
        # This would fail on Windows if the file is still locked.

        # This should succeed without exceptions.
        remove(local_video_filename)

    red.close()
    green.close()
    blue.close()
