
#~ from moviepy.video.VideoClip import VideoClip
from moviepy.video.ImageClip import ImageClip, ColorClip, TextClip
from io import VideoFileClip

try:
    import pygame as pg
    pg.init()
    pg.display.set_caption('MoviePy')
except:
    print ("WARNING: Pygame not found. Previews and many other user" +
            " interfaces will not be enabled.")
