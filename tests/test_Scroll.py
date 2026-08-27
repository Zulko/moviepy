"""Scroll fx tests."""
import pytest

from moviepy import ColorClip
from moviepy import CompositeVideoClip
from moviepy.video.fx import Scroll


def test_Scroll(speed_multiplier: float = 1.0):

    # Testing Scroll effect with 9 ColorClips in a 3x3 grid.
    # 0 Red    - 3 Magenta  - 6 Orange
    # 1 Green  - 4 Cyan     - 7 Purple
    # 2 Blue   - 5 Yellow   - 8 Pink

    # Video dimensions
    COLOR_CLIP_WIDTH = 1280
    COLOR_CLIP_HEIGHT = 720
    FINAL_WIDTH = 1280
    FINAL_HEIGHT = 720

    # Create 9 ColorClips with different colors
    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
        (255, 255, 0),  # Yellow
        (255, 128, 0),  # Orange
        (128, 0, 255),  # Purple
        (255, 192, 203),  # Pink
    ]

    color_clips = []
    for i, color in enumerate(colors):
        clip = ColorClip(
            size=(COLOR_CLIP_WIDTH, COLOR_CLIP_HEIGHT),
            color=color,
            duration=10  # 10 second duration
        )
        color_clips.append(clip)

    # Position clips in 3 columns, 3 rows
    # Column 0: clips 0, 1, 2 (positions x=0)
    # Column 1: clips 3, 4, 5 (positions x=1280)
    # Column 2: clips 6, 7, 8 (positions x=2560)
    positioned_clips = []

    for i, clip in enumerate(color_clips):
        col = i % 3  # Column (0, 1, or 2)
        row = i // 3  # Row (0, 1, or 2)

        x_pos = col * COLOR_CLIP_WIDTH
        y_pos = row * COLOR_CLIP_HEIGHT

        positioned_clip = clip.with_position((x_pos, y_pos))
        positioned_clips.append(positioned_clip)

    # Create composite clip (3840 x 2160)
    composite_width = COLOR_CLIP_WIDTH * 3  # 3840
    composite_height = COLOR_CLIP_HEIGHT * 3  # 2160

    composite_clip = CompositeVideoClip(
        positioned_clips,
        size=(composite_width, composite_height)
    )

    # Create scroll effect
    # We want to scroll from top-left to bottom-right
    # Start at top-left corner (0, 0)
    # End at bottom-right corner (2560, 1440) - showing the bottom-right area

    scroll_distance_x = composite_width - FINAL_WIDTH  # 3840 - 1280 = 2560
    scroll_distance_y = composite_height - FINAL_HEIGHT  # 2160 - 720 = 1440

    scroll_duration = 10  # 10 seconds
    x_speed = speed_multiplier * scroll_distance_x / scroll_duration  # 256 pixels per second
    y_speed = speed_multiplier * scroll_distance_y / scroll_duration  # 144 pixels per second

    # Apply scroll effect
    scrolled_clip = composite_clip.with_effects([
        Scroll(
            w=FINAL_WIDTH,
            h=FINAL_HEIGHT,
            x_speed=x_speed,
            y_speed=y_speed,
            x_start=0,
            y_start=0
        )
    ])

    # Verify the last frame before writing
    last_frame_time = scrolled_clip.duration - 0.1  # Get frame just before the end
    last_frame = scrolled_clip.get_frame(last_frame_time)

    # Get center pixel
    center_x = FINAL_WIDTH // 2
    center_y = FINAL_HEIGHT // 2
    center_pixel = last_frame[center_y, center_x]

    expected_pink = (255, 192, 203)
    # Convert center_pixel to int to avoid uint8 overflow issues
    center_pixel_int = [int(center_pixel[i]) for i in range(3)]
    is_pink = all(abs(center_pixel_int[i] - expected_pink[i]) < 10 for i in range(3))
    assert is_pink, "Center pixel is not pink!"

    # Clean up
    for clip in color_clips:
        clip.close()
    composite_clip.close()
    scrolled_clip.close()


def test_perfect_speed():

    # The video should
    # 1. Start at top-left (Red)
    # 2. Scroll diagonally through the 3x3 grid
    # 3. Move through: Red → Green → Blue → Magenta → Cyan → Yellow → Orange → Purple → Pink
    # 4. End at bottom-right (Pink)
    test_Scroll(1.0)


def test_slow_speed():

    # This one should not quite make it to full pink, but pink should still be in the center pixel
    test_Scroll(0.8)


def test_fast_speed():

    # This one should stop at full pink and not scroll anymore
    test_Scroll(3.0)


if __name__ == "__main__":

    pytest.main()
