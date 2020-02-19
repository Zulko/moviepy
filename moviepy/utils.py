from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip

def close_all_clips(objects='globals', types=('audio', 'video', 'image')):
    if objects == 'globals':
        objects = globals()
    if hasattr(objects, 'values'):
        objects = objects.values()
    types_tuple = tuple([
        {'audio': AudioFileClip,
         'video': VideoFileClip,
         'image': ImageClip}[t]
        for t in types
    ])
    for obj in objects:
        if isinstance(obj, types_tuple):
            obj.close()
