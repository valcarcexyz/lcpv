import numpy as np
import time

# our functions to preprocess data
from .lens_corrector import correct_lens_distortion, correct_perspective
from .filters import opening_filter, median_filter
# and the camera abstraction layer
from .camera import Camera

# for the parallel processing
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp
from threading import Thread

# particle velocimetry stuff
from openpiv.pyprocess import extended_search_area_piv, get_coordinates

# progress bar
import tqdm


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
        """Runs the complete experiment, parallel ready. It's threaded-based due to the memory sharing
        that it's needed. The code runs the following:

        1. Run the camera capture thread, adding the frames to a thread-safe Queue
        2. While the camera is running, process the results

        Params:
        =======
        :param resolution: tuple[int]
            The camera resolution
        :param framerate: int
            The framerate of the camera capture. If the frequency is too much, it just will take more seconds, i.e. if
            50fps requested, but the camera only captures@24fps, it will capture for 2 seconds.
        :param seconds: int
            How long to capture the experiment.
        :param camera_params: dict.
            If lens correction desired, must include the following keys:
                - cameraMatrix
                - distCoeff
            If perspective correction desired, must include:
                - originalPoints
                - destinationPoints
            values of the dict *must* by np.ndarray objects. If none of the keys are provided, the preprocessing
            will simply be ignored.
        :param kwargs: OpenPIV args, minimum arguments required are:
            - window_size: int
            - search_area_size: int
            - overlap: int
            Refer to (OpenPIV documentation)[1] for further details.

        [1]: http://www.openpiv.net/openpiv-python/
        """
        assert ("window_size" in kwargs) and ("search_area_size" in kwargs) and ("overlap" in kwargs), \
            "Minimum args include window_size, search_area_size and overlap"

        # Definition of the camera thread to capture the data (-data producer-)
        camera_capture_thread = Thread(
            target=self.camera.start_recording,
            args=(resolution, framerate, seconds, self.queue_frames)
        )
        # start the camera thread
        camera_capture_thread.start()

        # we need to provide some time to warm up the camera
        time.sleep(1)  # more than enough, it should be enough with 0.5 seconds.

        # full multiprocessing object
        futures = []
        with ThreadPoolExecutor(self.NUM_CPU-1) as executor:
            while self.queue.qsize() >= 2:
                frames = [self.queue.get() for _ in range(2)]
                futures.append(executor.submit(self.consume, *frames, camera_params, **kwargs))
                # enough time to ensure camera captures 2 new frames (does not slow down the processing time
                # as there are already jobs submitted and the computation time is well above 1 second).
                time.sleep(1)

            # now let's really consume the data
            for future in tqdm.tqdm(futures):
                self.results.append(future.result())

        # we need to consume the remaining elements of the queue (if there are any) in order
        # to be able to close the `camera_capture_process`. This can't occur more than twice.
        while not self.queue.empty():
            self.queue.get()

        # wait till camera is closed
        camera_capture_thread.join()

    @staticmethod
    def consume(frame0, frame1, camera_params: dict, **kwargs):
        """This is the frame consumer. Runs all the preprocessing (and the processing) to each one
        of the frames captured. The current implementation runs the following:

        1. Lens distortion correction (if `distCoeff` and `cameraMatrix` are provided inside the
            `camera_params` matrix).
        2. Perspective image correction (if `originalPoints` and `destinationPoints` are provided inside the
            `camera_params` matrix).
        3. Filter the results using an opening filter.
        4. OpenPIV particle velocimetry computation, with the provided kwargs.

        Params:
        =======
        frame0, frame1: np.ndarray
            The 2-D images, np.uint8 type, to run the computation on.
        camera_params: dict
            This dictionary provides the data needed to run the lens corrections, which include both lens
            correction and perspective correction. Based on the OpenCV library.
        **kwargs
            The remaining arguments which OpenPIV `extended_search_area_piv` runs with

        Returns:
        =======
        A tuple of (x, y, u, -v). Where (x, y) is the position and (u, -v) the velocity measured.
        """
        # to correct lens distortion, we check if both cameraMatrix and distCoeff are proviedd
        if ("cameraMatrix" in camera_params.keys()) and ("distCoeff" in camera_params.keys()):
            # we can safely run the lens distortion correction
            frame0, frame1 = [correct_lens_distortion(img,
                                                      camera_params["cameraMatrix"], camera_params["distCoeff"]
                                                      ) for img in [frame0, frame1]]
        # the same if we want to run the perspective correction
        if ("originalPoints" in camera_params.keys()) and ("destinationPoints" in camera_params.keys()):
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
        x, y = self.results[0][:2]
        results = np.array([(res[2], res[3]) for res in self.results])
        return x, y, np.nanmedian(results, axis=0)


if __name__ == "__main__":
    import json

    with open("../camera_calibration/parameters.json") as f:
        camera_params = dict(json.load(f))
    camera_params = {k: np.array(v) for k, v in camera_params.items()}
    l = LCPV()
    l.start(camera_params=camera_params, window_size=32, overlap=16, search_area_size=32)
    print(l.median_results)
