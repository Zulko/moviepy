from collections import defaultdict
from multiprocessing import Process, Queue

# Queue has been renamed to queue
try:
    from queue import Empty
except ImportError:
    from Queue import Empty

import signal
import platform
import numpy
import sys
import os


class Worker(object):

    def __init__(self, target, *args):
        self.queue_out = Queue()
        self.queue_in = Queue()
        self.target = target
        self.args = args
        self.process = Process(
            target=self.target,
            args=(self.queue_out, self.queue_in,) + self.args
        )
        self.process.daemon = True

    def start(self):
        try:
            return self.process.start()
        except BrokenPipeError as e:
            print("=" * 30)
            print("Ran into a broken pipe error")
            print("=" * 30)
            print("This can occur if you are calling functions " +
                  "directly from a module outside of any class/function")
            print("Make sure you have your script entry point inside " +
                  "a function, for example:")
            print("\n".join([
                "",
                "def main():",
                "    # code here",
                "",
                "if __name__ == '__main__':",
                "    main()"
            ]))
            print("=" * 30)
            print("Original exception:")
            print("=" * 30)
            raise

    def get(self):
        return self.queue_in.get()

    def put(self, val):
        return self.queue_out.put(val)

    def join(self):
        return self.process.join()


def iterframes_job(recv_queue, send_queue, times,
                   generator, generator_args, dtype):
    clip = generator(**generator_args)

    for current in iterate_frames_at_times(clip, times, dtype):
        send_queue.put(current, timeout=10)

        # Avoiding running ahead of the main thread and filling up memory
        # Timeout in 10 seconds in case the main thread has been killed
        try:
            recv_queue.get(timeout=10)
        except Empty:
            # For some reason sys.exit(), os._exit() doesn't work
            sig = signal.SIGTERM
            if platform.system() == "Windows":
                sig = signal.CTRL_C_EVENT
            os.kill(os.getpid(), sig)


def iterate_frames_at_times(clip, times, dtype):
    for time in times:
        frame = clip.get_frame(time)
        if (dtype is not None) and (frame.dtype != dtype):
            frame = frame.astype(dtype)
        yield time, frame


def get_clip_times(clip, fps):
    return numpy.arange(0, clip.duration, 1.0 / fps)


def iterframes(threads, clip, fps, dtype, with_times):
    attrs = {
        "clip": clip,
        "fps": fps,
        "dtype": dtype,
    }
    if threads < 1:
        generator = singlethread_iterframes
    else:
        generator = multithread_iterframes
        attrs["threads"] = threads

    for current in generator(**attrs):
        if with_times:
            yield current
        else:
            yield current[1]


def singlethread_iterframes(clip, fps, dtype):
    times = get_clip_times(clip, fps)
    for current in iterate_frames_at_times(clip, times, dtype):
        yield current


def multithread_iterframes(threads, clip, fps, dtype):
    times = get_clip_times(clip, fps)
    jobsets = defaultdict(list)
    for index, time in enumerate(times):
        jobsets[index % threads].append(time)

    workers = [
        Worker(
            iterframes_job,
            jobsets[i],
            clip.generator,
            clip.generator_args,
            dtype
        ) for i in range(threads)]

    for worker in workers:
        worker.start()

    for index, time in enumerate(times):
        current = workers[index % threads].get()
        workers[index % threads].put(True)
        yield current
        sys.stdout.flush()

    for worker in workers:
        worker.join()
