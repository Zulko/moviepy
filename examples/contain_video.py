"""Contain a local video in portrait and square canvases without cropping."""
import argparse
from pathlib import Path
from moviepy import ColorClip, CompositeVideoClip, VideoFileClip


def contain_clip(source, size, background=(232, 238, 233)):
    """Return a new canvas; the caller retains ownership of source."""
    width, height = size
    scale = min(width / source.w, height / source.h)
    fitted = source.resized(scale).with_position("center")
    canvas = ColorClip(size, color=background, duration=source.duration)
    return CompositeVideoClip([canvas, fitted], size=size)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("out"))
    parser.add_argument("--max-seconds", type=float, default=None)
    args = parser.parse_args()
    if args.max_seconds is not None and args.max_seconds <= 0:
        parser.error("--max-seconds must be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with VideoFileClip(str(args.input)) as original:
        end = (
            original.duration
            if args.max_seconds is None
            else min(original.duration, args.max_seconds)
        )
        source = original.subclipped(0, end)
        formats = [("portrait", (1080, 1920)), ("square", (1080, 1080))]
        for name, size in formats:
            with contain_clip(source, size) as variant:
                variant.write_videofile(
                    str(args.output_dir / f"{name}.mp4"),
                    fps=30,
                    codec="libx264",
                    audio_codec="aac",
                    pixel_format="yuv420p",
                )


if __name__ == "__main__":
    main()
