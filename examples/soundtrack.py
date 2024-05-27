"""A simple test script on how to put a soundtrack to a movie."""

from moviepy import *


# We load a movie and replace the sound with some music:

movie = VideoFileClip("../../videos/dam.mov").with_audio(
    AudioFileClip("../../sounds/startars.ogg")
)


# If the soundtrack is longer than the movie, then at the end of the clip
# it will freeze on the last frame and wait for the clip to finish.
# If you don't want that, uncomment the next line:

# ~ movie.audio = movie.audio.with_duration(movie.duration)

movie.write_videofile("../../test_soundtrack.avi", codec="mpeg4")
