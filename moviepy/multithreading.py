

def multithread_write_videofile(
            filename, clip_generator, clip_generator_args={},
            ffmpeg_threads=6, moviepy_threads=2, **kwargs):
    clip = clip_generator(**clip_generator_args)
    clip.generator = clip_generator
    clip.generator_args = clip_generator_args

    kwargs.update({
        "filename": filename,
        "threads": ffmpeg_threads,
        "moviepy_threads": moviepy_threads
    })
    clip.write_videofile(**kwargs)
