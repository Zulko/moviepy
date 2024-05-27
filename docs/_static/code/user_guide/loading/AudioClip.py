from moviepy import *
import numpy as np

# Producing a sinewave of 440 Hz -> note A
make_frame_audio = lambda t: np.sin(440 * 2 * np.pi * t)

# AUDIO CLIPS
clip = AudioClip(make_frame_audio, duration=3)
