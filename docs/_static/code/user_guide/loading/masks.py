from moviepy import VideoClip, ImageClip, VideoFileClip
import numpy as np

# Random RGB noise image of 200x100
frame_function = lambda t: np.random.rand(100, 200)

# To define the VideoClip as a mask, just pass parameter is_mask as True
maskclip1 = VideoClip(frame_function, duration=4, is_mask=True)  # A random noise mask
maskclip2 = ImageClip("example_mask.jpg", is_mask=True)  # A fixed mask as jpeg
maskclip3 = VideoFileClip("example_mask.mp4", is_mask=True)  # A video as a mask

# Load our basic clip, resize to 200x100 and apply each mask
clip = VideoFileClip("example.mp4")
clip_masked1 = clip.with_mask(maskclip1)
clip_masked2 = clip.with_mask(maskclip2)
clip_masked3 = clip.with_mask(maskclip3)
