"""Let's create an audioclip from values in a numpy array."""

import numpy as np
from moviepy import AudioArrayClip

# We want to play these notes
notes = {"A": 440, "B": 494, "C": 523, "D": 587, "E": 659, "F": 698}

note_duration = 0.5
total_duration = len(notes) * note_duration
sample_rate = 44100  # Number of samples per second

note_size = int(note_duration * sample_rate)
n_frames = note_size * len(notes)


def frame_function(t, note_frequency):
    return np.sin(note_frequency * 2 * np.pi * t)


# At this point one could use this audioclip which generates the audio on the fly
# clip = AudioFileClip(frame_function)

# We generate all frames timepoints

audio_frame_values = [
    2 * [frame_function(t, freq)]
    for freq in notes.values()
    for t in np.arange(0, note_duration, 1.0 / sample_rate)
]
# Create an AudioArrayClip from the audio samples
audio_clip = AudioArrayClip(np.array(audio_frame_values), fps=sample_rate)

# Write the audio clip to a WAV file
audio_clip.write_audiofile("result.wav", fps=44100)
