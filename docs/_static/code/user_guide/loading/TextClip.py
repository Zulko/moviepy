from moviepy import TextClip

font = "./example.ttf"

# First we use as string and let system autocalculate clip dimensions to fit the text
# we set clip duration to 2 secs, if we do not, it got an infinite duration
txt_clip1 = TextClip(
    font=font,
    text="Hello World !",
    font_size=30,
    color="#FF0000",  # Red
    bg_color="#FFFFFF",
    duration=2,
)
# This time we load text from a file, we set a fixed size for clip and let the system find best font size,
# allowing for line breaking
txt_clip2 = TextClip(
    font=font,
    filename="./example.txt",
    size=(500, 200),
    bg_color="#FFFFFF",
    method="caption",
    color=(0, 0, 255, 127),
)  # Blue with 50% transparency

# we set duration, because by default image clip are infinite, and we cannot render infinite
txt_clip2 = txt_clip2.with_duration(2)
# ImageClip have no FPS either, so we must defined it
txt_clip1.write_videofile("result1.mp4", fps=24)
txt_clip2.write_videofile("result2.mp4", fps=24)
