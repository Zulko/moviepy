from moviepy import AudioClip
import numpy as np


def audio_frame(t):
    """Producing a sinewave of 440 Hz -> note A"""
    return np.sin(440 * 2 * np.pi * t)


audio_clip = AudioClip(frame_function=audio_frame, duration=3)
