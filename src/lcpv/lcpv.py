# our files
import numpy as np

from lens_corrector import correct_lens_distortion, correct_perspective
from filters import opening_filter, median_filter
from camera import Camera

# for the parallel processing
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp


class LCPV:
    """"""
    NUM_CPU = mp.cpu_count()

    def __init__(self):
        """Constructor"""
        self.queue = mp.Queue()
        self.camera = Camera()

    def start(self, resolution: tuple = (1920, 1080), framerate: int = 24, seconds: int = 1):
        """Run!"""
        # FIXME: may be better idea to run the process output in the consumer, more than in the producer,
        # to ensure framerate.
        # TODO: run in a separated process
        self.camera.start_recording(resolution=resolution,
                                    framerate=framerate,
                                    seconds=seconds,
                                    process_output=self.queue_frames)

    def consume(self, frames):
        """Frames consumer"""

    def queue_frames(self, frame: np.ndarray):
        """Method to save the frames to the queue"""
        # TODO: add the parameter from the json or by hand
        image_lens_corrected = correct_lens_distortion(frame)
        image_perspective_corrected = correct_perspective(image_lens_corrected)
        image_masked = opening_filter(image_perspective_corrected)
        self.queue.mutex.acquire()
        self.queue.put_nowait(image_masked)
        self.queue.mutex.release()


if __name__ == "__main__":
    l = LCPV()
