from moviepy import VideoFileClip
from moviepy import vfx, afx

# from os import listdir
# from os.path import isfile, join

# import os
# dir = os.path.dirname(__file__)
# onlyfiles = [f for f in listdir(dir) if isfile(join(dir, f))]

# import pathlib
# print(globals())
# print(pathlib.Path('./').resolve())
# print(onlyfiles)
myclip = VideoFileClip("example.mp4")
myclip = myclip.with_end(5) # stop the clip after 5 sec
myclip = myclip.without_audio() # remove the audio of the clip
