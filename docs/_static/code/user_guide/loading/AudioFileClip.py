from moviepy import *
import numpy as np

# Works for audio files, but also videos file where you only want the keep the audio track
clip = AudioFileClip("example.wav")
clip.write_audiofile("./result.wav")
