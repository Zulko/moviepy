from moviepy import *

# clip.close() is implicitly called, so the lock on my_audiofile.mp3 file
# is immediately released.
try:
    with AudioFileClip("example.wav") as clip:
        raise Exception("Let's simulate an exception")
except Exception as e:
    print("{}".format(e))
