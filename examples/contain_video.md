# Contain a video in delivery canvases

Run from the repository root with MoviePy2.x installed:

```sh
python examples/contain_video.py input.mp4 --output-dir out
```

Writes portrait (1080x1920) and square (1080x1080) MP4s. The entire input stays visible: wide video receives top/bottom padding in a portrait canvas; portrait video receives side padding in a square canvas. No cropping or stretching. The source audio and duration are preserved. Use `--max-seconds 1` for a quick preview. The script closes readers/writers after use and encodes H.264/AAC with yuv420p.

Change `contain_clip`'s RGB background argument for a different canvas color. Provide any local video you have permission to edit. This recipe makes no network calls and needs no credentials, external fonts or media downloads.

Contributed by [VideoGen](https://videogen.io/). A standalone integration demonstrating generated video followed by this local post-processing step, with runnable tests and synthetic sample media, is available in [video-workflow-recipes](https://github.com/video-gen/video-workflow-recipes).
