
       
from moviepy.editor import ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

image_path = "ismi timeshop ve trend olan seyleri satacagim.jpg"

clip = ImageClip(image_path, duration=6).resize(height=720)

def zoom(t):
    return 1 + 0.05 * t  # yakınlaşma efekti
zoom_clip = clip.resize(zoom)

def make_welcome_frame(size):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("DejaVuSerif-Bold.ttf", 100)
    text = "Welcome"
    text_size = draw.textsize(text, font=font)
    pos = ((size[0]-text_size[0])//2, (size[1]-text_size[1])//2)
    draw.text(pos, text, font=font, fill=(255, 215, 0))  # altın rengi
    return np.array(img)

welcome_clip = (ImageClip(make_welcome_frame((1280, 720)), ismask=False)
                .set_duration(2)
                .set_start(4)
                .set_pos("center"))

final = CompositeVideoClip([zoom_clip, welcome_clip])
final.write_videofile("timeshop_welcome.mp4", fps=24, codec="libx264")
