import threading
import time

from moviepy import VideoFileClip
from moviepy.utils import stop_processing_video


def edit_video(output):
    """Just to start some process"""
    vid = VideoFileClip("media/sintel_with_14_chapters.mp4")
    vid.write_videofile(output)


vid1_filename = "examples/first_vid.mp4"
vid2_filename = "second_vid.mp4"
vid3_filename = "third_vid.mp4"

t1 = threading.Thread(target=edit_video, args=[vid1_filename])
t2 = threading.Thread(target=edit_video, args=[vid2_filename])
t3 = threading.Thread(target=edit_video, args=[vid3_filename])

t1.start()
t2.start()
t3.start()

time.sleep(1)
stop_processing_video(vid1_filename)
# stop_processing_video(vid2_filename)
stop_processing_video(vid3_filename)
