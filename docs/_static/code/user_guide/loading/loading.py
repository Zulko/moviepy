from moviepy import (
    VideoClip,
    VideoFileClip,
    ImageSequenceClip,
    ImageClip,
    TextClip,
    ColorClip,
    AudioFileClip,
    AudioClip,
)
import numpy as np

# Define some constants for later use
black = (255, 255, 255)  # RGB for black


def get_frame(t):
    """Random noise image of 200x100"""
    return np.random.randint(low=0, high=255, size=(100, 200, 3))


def get_frame_audio(t):
    """A note by producing a sinewave of 440 Hz"""
    return np.sin(440 * 2 * np.pi * t)


# Now lets see how to load different type of resources !

# VIDEO CLIPS
# for custom animations, where get_frame is a function returning an image
# as numpy array for a given time
clip = VideoClip(get_frame, duration=5)
clip = VideoFileClip("example.mp4")  # for videos
# for a list or directory of images to be used as a video sequence
clip = ImageSequenceClip("example_img_dir", fps=24)
clip = ImageClip("example.png")  # For a picture
# To create the image of a text
clip = TextClip(font="./example.ttf", text="Hello!", font_size=70, color="black")
# a clip of a single unified color, where color is a RGB tuple/array/list
clip = ColorClip(size=(460, 380), color=black)

# AUDIO CLIPS
# for audio files, but also videos where you only want the keep the audio track
clip = AudioFileClip("example.wav")
# for custom audio, where get_frame is a function returning a
# float (or tuple for stereo) for a given time
clip = AudioClip(get_frame_audio, duration=3)
