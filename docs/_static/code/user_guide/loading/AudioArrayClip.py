import numpy as np
from moviepy import *

# We want to play those notes
notes = {"A": 440, "B": 494, "C": 523, "D": 587, "E": 659, "F": 698}

note_duration = 0.5
total_duration = len(notes) * note_duration
sample_rate = 44100  # Number of samples per second

note_size = int(note_duration * sample_rate)
total_size = note_size * len(notes)


def make_frame(t, note_frequency):
    return np.sin(note_frequency * 2 * np.pi * t)


# We generate all frames timepoints
times = np.linspace(0, total_duration, total_size)

# We make an array of size N*1, where N is the number of frames * total duration
audio_array = np.zeros((total_size, 2))
i = 0
for note, frequency in notes.items():
    for _ in range(note_size):
        audio_array[i][0] = make_frame(times[i], frequency)
        i += 1

# Create an AudioArrayClip from the audio samples
audio_clip = AudioArrayClip(audio_array, fps=sample_rate)

# Write the audio clip to a WAV file
audio_clip.write_audiofile("result.wav", fps=44100)
