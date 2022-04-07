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
        # Definition of the camera process to capture the data (-data producers-)
        camera_capture_process = mp.Process(
            target=self.camera.start_recording,
            args=(resolution, framerate, seconds, self.queue_frames)
        )
        # start the camera process
        camera_capture_process.start()

        # Definition of the consumer processes
        qsize = 0
        futures = []
        with ProcessPoolExecutor(max_workers=self.NUM_CPU-1) as executor:
            while self.camera.running.value or (qsize >= 2):
                # we have data to consume!
                # We first lock the queue, and then get the desired frames
                self.queue.mutex.acquire()
                frame0 = self.queue.queue.popleft()
                frame1 = self.queue.queue[0]
                self.queue.mutex.release()

                # we can create and call a new process to run on this frames
                futures.append(executor.submit(self.consume, frame0, frame1))

                # update the qsize:
                qsize = self.queue.qsize()

            # now we ensure the results are really processed
            for future in futures:
                future.result()

        # wait till camera is closed
        camera_capture_process.join()

        # # TODO: run in a separated process
        # self.camera.start_recording(resolution=resolution,
        #                             framerate=framerate,
        #                             seconds=seconds,
        #                             process_output=self.queue_frames)

    def consume(self, frame0, frame1):
        """Frames consumer"""
        # TODO: run on both frames
        # TODO: compute openpiv
        image_lens_corrected = correct_lens_distortion(frame0)
        image_perspective_corrected = correct_perspective(image_lens_corrected)
        image_masked = opening_filter(image_perspective_corrected)
        return image_masked

    def queue_frames(self, frame: np.ndarray):
        """Method to save the frames to the queue"""
        # self.queue.mutex.acquire()
        self.queue.put(frame)  # FIXME: or put_nowait()? TRY IT
        # self.queue.mutex.release()


if __name__ == "__main__":
    l = LCPV()
