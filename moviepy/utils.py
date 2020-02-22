from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip


CLIP_TYPES = {
    'audio': AudioFileClip,
    'video': VideoFileClip,
    'image': ImageClip,
}

def close_all_clips(objects='globals', types=('audio', 'video', 'image')):
    if objects == 'globals':
        objects = globals()
    if hasattr(objects, 'values'):
        objects = objects.values()
    types_tuple = tuple(CLIP_TYPES[key] for key in types)
    for obj in objects:
        if isinstance(obj, types_tuple):
            obj.close()
