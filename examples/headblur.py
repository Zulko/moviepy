#!/usr/bin/env python

# https://zulko.github.io/moviepy/examples/headblur.html

import sys
import pathlib
import pickle
import moviepy.editor
import moviepy.video.tools.tracking

# Two arguments: movie_in [subclip_s]
# You can try (for checking the size of the blur) by setting subclip_s=1
# Then delete the .dat file and do the whole file without second argument
movie_in=sys.argv[1]
if len(sys.argv)==3:
 subclip_s=float(sys.argv[2])
else:
 subclip_s=None

trackingfile=pathlib.Path(movie_in+'.dat')
# Often a subclip (min,sec) is wanted, and if it's only for testing...
clip = moviepy.editor.VideoFileClip(movie_in)
if subclip_s is not None:
 clip=clip.subclip((0,0),(0,subclip_s))

# MANUAL TRACKING OF THE HEAD

# The next lines are for the manual tracking and its saving
# to a file, which is done if tracking.dat does not yet exist.
if not trackingfile.exists():
 # This is a list of moviepy.video.tools.interpolators.Trajectory
 tracking=moviepy.video.tools.tracking.manual_tracking(clip, fps=6)[0]
 with trackingfile.open('wb') as f:
  pickle.dump(tracking,f)

# IF THE MANUAL TRACKING HAS BEEN PREVIOUSLY DONE,
# LOAD THE TRACKING DATA AND CONVERT IT TO FUNCTIONS x(t),fy(t)

with trackingfile.open('rb') as f:
 tracking = pickle.load(f)

# BLUR HEAD IN THE CLIP

# /usr/lib/python3.7/site-packages/moviepy/video/fx/headblur.py
# r_zone is the radius and r_blur the intensity of the blurring -
# r_blur must be integer but is set to 2*r_zone/3 in the code if unset,
# creating a float leading to an error, so rather set it explicitly here...
clip_blurred = clip.fx(moviepy.editor.vfx.headblur, tracking.xi, tracking.yi, 50, 20)

clip_blurred.write_videofile(movie_in+'_blurred.mp4', bitrate="3000k")
