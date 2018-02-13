from moviepy.editor import *
from moviepy.video.tools.drawing import circle

clip = VideoFileClip("../../videos/badl-0006.mov", audio=False).\
           subclip(26,31).\
           add_mask()
           
w,h = clip.size

# The mask is a circle with vanishing radius r(t) = 800-200*t               
clip.mask.get_frame = lambda t: circle(screensize=(clip.w,clip.h),
                                       center=(clip.w/2,clip.h/4),
                                       radius=max(0,int(800-200*t)),
                                       col1=1, col2=0, blur=4)


the_end = TextClip("The End", font="Amiri-bold", color="white",
                   fontsize=70).set_duration(clip.duration)

final = CompositeVideoClip([the_end.set_pos('center'),clip],
                           size =clip.size)
                           
final.write_videofile("../../theEnd.avi")
