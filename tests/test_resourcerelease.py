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
from .test_helper import TMP_DIR

from moviepy.video.compositing.CompositeVideoClip import clips_array
from moviepy.video.VideoClip import ColorClip
from moviepy.video.io.VideoFileClip import VideoFileClip


def test_release_of_file_via_close():
    # Create a random video file.
    red = ColorClip((256, 200), color=(255, 0, 0))
    green = ColorClip((256, 200), color=(0, 255, 0))
    blue = ColorClip((256, 200), color=(0, 0, 255))

    red.fps = green.fps = blue.fps = 10

    # Repeat this so we can see no conflicts.
    for i in range(3):
        # Get the name of a temporary file we can use.
        local_video_filename = join(
            TMP_DIR,
            "test_release_of_file_via_close_%s.mp4" % int(time.time())
        )

        clip = clips_array([[red, green, blue]]).set_duration(0.5)
        clip.write_videofile(local_video_filename)

        # Open it up with VideoFileClip.
        video = VideoFileClip(local_video_filename)
        video.close()
        clip.close()

        # Now remove the temporary file.
        # This would fail on Windows if the file is still locked.

        # This should succeed without exceptions.
        remove(local_video_filename)

    red.close()
    green.close()
    blue.close()
