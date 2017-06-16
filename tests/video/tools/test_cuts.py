from moviepy.editor import ColorClip, concatenate_videoclips
from moviepy.video.tools.cuts import detect_scenes


def test_detect_scenes__red_green():
    """
    Test that a cut is detected between concatenated red and green clips
    """
    red = ColorClip((640, 480), color=(255, 0, 0)).set_duration(1)
    green = ColorClip((640, 480), color=(0, 200, 0)).set_duration(1)
    video = concatenate_videoclips([red, green])

    cuts, luminosities = detect_scenes(video, fps=10, progress_bar=False)

    assert len(cuts) == 2
