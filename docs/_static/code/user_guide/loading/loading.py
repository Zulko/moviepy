from moviepy import *
import numpy as np

# Define some constants for later use
black = (255, 255, 255)  # RGB for black
# Random noise image of 200x100
make_frame = lambda t: np.random.randint(low=0, high=255, size=(100, 200, 3))
# A note by producing a sinewave of 440 Hz
make_frame_audio = lambda t: np.sin(440 * 2 * np.pi * t)

# Now lets see how to load different type of resources !

# VIDEO CLIPS`
clip = VideoClip(
    make_frame, duration=5
)  # for custom animations, where make_frame is a function returning an image as numpy array for a given time
clip = VideoFileClip("example.mp4")  # for videos
clip = ImageSequenceClip(
    "example_img_dir", fps=24
)  # for a list or directory of images to be used as a video sequence
clip = ImageClip("example.png")  # For a picture
clip = TextClip(
    font="./example.ttf", text="Hello!", font_size=70, color="black"
)  # To create the image of a text
clip = ColorClip(
    size=(460, 380), color=black
)  # a clip of a single unified color, where color is a RGB tuple/array/list

# AUDIO CLIPS
clip = AudioFileClip(
    "example.wav"
)  # for audio files, but also videos where you only want the keep the audio track
clip = AudioClip(
    make_frame_audio, duration=3
)  # for custom audio, where make_frame is a function returning a float (or tuple for stereo) for a given time
