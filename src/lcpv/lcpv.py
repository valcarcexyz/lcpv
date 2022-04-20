import numpy as np
import time

# our functions to preprocess data
from lens_corrector import correct_lens_distortion, correct_perspective
from filters import opening_filter, median_filter
# and the camera abstraction layer
from camera import Camera

# for the parallel processing
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp
from threading import Thread

# particle velocimetry stuff
from openpiv.pyprocess import extended_search_area_piv, get_coordinates


class LCPV:
    """
    Class abstraction between users and both the Raspberry Camera interface and the OpenPIV library.
    It provides an easy-to-use, parallel by default API, meant to be used within a Raspberry Pi (preferably the 4th
    model).
    """
    NUM_CPU = mp.cpu_count()

    def __init__(self):
        """Constructor"""
        manager = mp.Manager()
        self.queue = manager.Queue()
        self.camera = Camera()
        self.results = []

    def start(self,
              resolution: tuple = (1920, 1080), framerate: int = 24, seconds: int = 1,
              camera_params: dict = {}, **kwargs):
        """Run!

        Params:
        =======
        ...
        camera_params: dict. Must include the following keys:
            - cameraMatrix
            - distCoeff
            - originalPoints
            - destinationPoints
        **kwargs => openpiv args, minumum kwargs are:
            - window_size
            - search_area_size
            - overlap
        """
        assert ("window_size" in kwargs) and ("search_area_size" in kwargs) and ("overlap" in kwargs), \
            "Minimum args include window_size, search_area_size and overlap"

        # Definition of the camera process to capture the data (-data producers-)
        camera_capture_process = Thread(
            target=self.camera.start_recording,
            args=(resolution, framerate, seconds, self.queue_frames)
        )
        # start the camera process
        camera_capture_process.start()

        # we need to provide some time to start the camera
        time.sleep(2)  # more than enough

        # full multiprocessing object
        futures = []
        with ThreadPoolExecutor(self.NUM_CPU, initargs=(self.queue,)) as executor:
            # process that will run the camera-things
            camera_thread = executor.submit(self.camera.start_recording,
                                            args=(resolution, framerate, seconds, self.queue_frames))

            time.sleep(2)  # time to start the camera
            # now the logic to run everything inside the pool
            while self.queue.qsize() >= 2:
                if len(futures) == 3:
                    for _ in range(len(futures)):
                        self.results.append(futures.pop().result())
                else:
                    frames = [self.queue.get() for _ in range(2)]
                    futures.append(executor.submit(self.consume, (*frames, camera_params), kwargs))

                # # we have some data to consume!
                # if self.queue.qsize() < 2:  # ensure we have some data to consume in pairs
                #     time.sleep(0.05)  # average time to get a new frame
                # frames = [self.queue.get() for _ in range(2)]
                # futures.append(pool.apply_async(self.consume, (*frames, camera_params), kwargs))

            # # now let's really consume the data
            # for future in futures:
            #     future.get()

        # # Pool process of data consumers
        # futures = []
        # with ProcessPoolExecutor(max_workers=self.NUM_CPU-1) as executor:  # -1 as we need 1 core for the camera
        #     while self.camera.running.value or (self.queue.qsize() >= 2):
        #         # we have some data to consume!
        #         if self.queue.qsize() < 2:  # ensure we have some data to consume in pairs
        #             time.sleep(0.05)  # average time to get a new frame
        #         frames = [self.queue.get() for _ in range(2)]
        #         # we can create and call a new process to run on this frames
        #         futures.append(executor.submit(self.consume, *frames, camera_params, **kwargs))
        #
        #     # now we ensure the results are really processed
        #     for future in futures:
        #         self.results.append(future.result())

        # we need to consume the remaining elements of the queue (if there are any) in order
        # to be able to close the `camera_capture_process`. This can't occur more than twice.
        while not self.queue.empty():
            self.queue.get()

        # wait till camera is closed
        camera_capture_process.join()

    def consume(self, frame0, frame1, camera_params: dict, **kwargs):
        """Frames consumer"""
        # to correct lens distortion, we check if both cameraMatrix and distCoeff are present
        if ("cameraMatrix" in camera_params.keys()) and ("distCoeff" in camera_params.keys()):
            # we can safely run the lens distortion correction
            frame0, frame1 = [correct_lens_distortion(img,
                                                      camera_params["cameraMatrix"], camera_params["distCoeff"]
                                                      ) for img in [frame0, frame1]]
        if ("originalPoints" in camera_params.keys()) and ("destinationPoints" in camera_params.keys()):
            # we can alse correct the perspective distortion
            frame0, frame1 = [correct_perspective(img,
                                                  camera_params["originalPoints"], camera_params["destinationPoints"]
                                                  ) for img in [frame0, frame1]]

        # now we can binarize images
        frame0, frame1 = [opening_filter(img) for img in [frame0, frame1]]

        # and finally run the openpiv computation
        u, v, s2n = extended_search_area_piv(frame0, frame1, **kwargs)
        x, y = get_coordinates(image_size=frame0.shape,
                               search_area_size=kwargs["search_area_size"],
                               overlap=kwargs["overlap"])
        valid = s2n < np.percentile(s2n, 5)
        return x[valid], y[valid], u[valid], -v[valid]

    def queue_frames(self, frame: np.ndarray):
        """Method to save the frames to the queue"""
        self.queue.put(frame)

    @property
    def median_results(self):
        """
        return x, y, median(u), median(v)
        """
        # TODO: check if median is correct
        x, y = self.results[0][:2]
        results = np.array([(res[2], res[3]) for res in self.results])
        return x, y, np.nanmedian(results, axis=0)  # axis = 0?


if __name__ == "__main__":
    import json

    with open("../camera_calibration/parameters.json") as f:
        camera_params = dict(json.load(f))
    camera_params = {k: np.array(v) for k, v in camera_params.items()}
    l = LCPV()
    l.start(camera_params=camera_params, window_size=32, overlap=16, search_area_size=32)
    print(l.median_results)
