from moviepy import *

with AudioFileClip("example.mp3") as clip:
    raise Exception("Let's simulate an exception")

# clip.close() is implicitly called, so the lock on my_audiofile.mp3 file is immediately released.