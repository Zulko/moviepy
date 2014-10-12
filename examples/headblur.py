import pickle

from moviepy.editor import *
from moviepy.video.tools.tracking import manual_tracking, to_fxfy


# LOAD THE CLIP (subclip 6'51 - 7'01 of a chaplin movie)
clip = VideoFileClip("../../videos/chaplin.mp4").subclip((6,51.7),(7,01.3))

# MANUAL TRACKING OF THE HEAD

# the three next lines are for the manual tracking and its saving
# to a file, it must be commented once the tracking has been done
# (after the first run of the script for instance).
# Note that we save the list (ti,xi,yi), not the functions fx and fy
# (that we will need) because they have dependencies.

#txy, (fx,fy) = manual_tracking(clip, fps=6)
#with open("../../chaplin_txy.dat",'w+') as f:
#    pickle.dump(txy)



# IF THE MANUAL TRACKING HAS BEEN PREVIOUSLY DONE,
# LOAD THE TRACKING DATA AND CONVERT IT TO FUNCTIONS x(t),fy(t)

with open("../../chaplin_txy.dat",'r') as f:
    fx,fy = to_fxfy( pickle.load(f) )


# BLUR CHAPLIN'S HEAD IN THE CLIP

clip_blurred = clip.fx( vfx.headblur, fx, fy, 25)


# Generate the text, put in on a grey background

txt = TextClip("Hey you ! \n You're blurry!", color='grey70',
               size = clip.size, bg_color='grey20',
               font = "Century-Schoolbook-Italic", fontsize=40)
               
               
# Concatenate the Chaplin clip with the text clip, add audio

final = concatenate_videoclips([clip_blurred,txt.set_duration(3)]).\
          set_audio(clip.audio)

# We write the result to a file. Here we raise the bitrate so that
# the final video is not too ugly.

final.write_videofile('../../blurredChaplin.avi', bitrate="3000k")
